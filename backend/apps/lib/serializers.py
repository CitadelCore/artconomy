import base64, uuid

from avatar.templatetags.avatar_tags import avatar_url
from django.conf import settings
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework_bulk import BulkSerializerMixin, BulkListSerializer

from apps.lib.models import Comment, Notification, Event, CHAR_TAG, SUBMISSION_CHAR_TAG, Tag, REVISION_UPLOADED, \
    ORDER_UPDATE, SALE_UPDATE, COMMENT
from apps.profiles.models import User, ImageAsset, Character
from apps.sales.models import Revision


class UserInfoSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    def __init__(self, request=None, *args, **kwargs):
        # For compatibility with main User serializer
        super().__init__(*args, **kwargs)

    def get_avatar_url(self, obj):
        return avatar_url(obj)

    class Meta:
        model = User
        fields = ('id', 'username', 'avatar_url', 'biography')
        read_only_fields = ('id', 'username', 'avatar_url')


class RelatedUserSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    def __init__(self, request=None, *args, **kwargs):
        # For compatibility with main User serializer
        super().__init__(*args, **kwargs)

    def get_avatar_url(self, obj):
        return avatar_url(obj)

    class Meta:
        model = User
        fields = ('id', 'username', 'avatar_url')
        read_only_fields = ('id', 'username', 'avatar_url')


def notification_serialize(obj):
    if obj is None:
        return None
    if hasattr(obj, 'notification_serialize'):
        return obj.notification_serialize()
    return {obj.__class__.__name__: obj.id}


def notification_display(obj):
    """
    For determining which icon is used in the notification area.
    """
    if hasattr(obj, 'notification_display'):
        return obj.notification_display()
    return notification_serialize(obj)


def get_link(obj, request):
    if obj is None:
        return None
    if hasattr(obj, 'notification_link'):
        return obj.notification_link(request)
    return None


def get_display_name(obj, request):
    if obj is None:
        return '<removed>'
    if hasattr(obj, 'notification_name'):
            return obj.notification_name(request) or 'Untitled'
    return 'Unknown'


class EventTargetRelatedField(serializers.RelatedField):
    """
    A custom field to use for the `content_object` generic relationship.

    Invokes the notification_serialize function on the target.
    """

    def to_representation(self, value):
        """
        Serialize tagged objects to a simple textual representation.
        """
        return notification_serialize(value)


# Custom image field - handles base 64 encoded images
class Base64ImageField(serializers.ImageField):
    def __init__(self, *args, **kwargs):
        self.thumbnail_namespace = kwargs.pop('thumbnail_namespace', '')
        super().__init__(*args, **kwargs)

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            # base64 encoded image - decode
            fmt, image_string = data.split(';base64,')  # format ~= data:image/X,
            ext = fmt.split('/')[-1]  # guess file extension
            auto_id = uuid.uuid4()
            data = ContentFile(base64.b64decode(image_string), name=auto_id.urn[9:] + '.' + ext)
        result = super(Base64ImageField, self).to_internal_value(data)
        return result

    def to_representation(self, value):
        if not value:
            return None
        values = {}

        for key in settings.THUMBNAIL_ALIASES[self.thumbnail_namespace]:
            values[key] = value[key].url

        values['full'] = value.url

        request = self.context.get('request', None)
        if request is not None:
            values = {
                key: request.build_absolute_uri(value) for key, value in values.items()
            }

        return values


class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class CommentSerializer(serializers.ModelSerializer):
    user = RelatedUserSerializer(read_only=True)
    children = RecursiveField(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'text', 'created_on', 'edited_on', 'user', 'children', 'edited', 'deleted')
        read_only_fields = ('id', 'created_on', 'edited_on', 'user', 'children', 'edited', 'deleted')


def get_user(user_id):
    try:
        return RelatedUserSerializer(instance=User.objects.get(id=user_id)).data
    except User.DoesNotExist:
        return None


def char_tag(obj, _):
    value = obj.data
    from apps.profiles.serializers import ImageAssetSerializer
    try:
        asset = ImageAssetSerializer(instance=ImageAsset.objects.get(id=value['asset'])).data
    except ImageAsset.DoesNotExist:
        asset = None
    try:
        user = RelatedUserSerializer(instance=User.objects.get(id=value['user'])).data
    except User.DoesNotExist:
        user = None
    return {'user': user, 'asset': asset}


def submission_char_tag(obj, _):
    value = obj.data
    from apps.profiles.serializers import CharacterSerializer
    try:
        character = CharacterSerializer(instance=Character.objects.get(id=value['character'])).data
    except Character.DoesNotExist:
        character = None
    user = get_user(value['user'])
    return {'character': character, 'user': user}


def revision_uploaded(obj, _):
    value = obj.data
    from apps.sales.serializers import RevisionSerializer
    try:
        revision = RevisionSerializer(instance=Revision.objects.get(id=value['revision'])).data
    except Revision.DoesNotExist:
        revision = None
    return {'revision': revision}


def order_update(obj, _):
    from apps.sales.serializers import RevisionSerializer, ProductSerializer
    revision = obj.target.revision_set.all().last()
    if revision is None:
        display = ProductSerializer(instance=obj.target.product).data
    else:
        display = RevisionSerializer(instance=revision).data
    return {'display': display}


def comment_made(obj, context):
    comment = Comment.objects.filter(id__in=obj.data['comments']).order_by('-id').first()
    top = comment
    while top.parent:
        top = top.parent
    target = top.content_object
    is_thread = bool((not comment.content_object) and comment.parent)
    commenters = Comment.objects.filter(
        id__in=obj.data['comments'] + obj.data['subcomments']).order_by('user__username').distinct('user__username')

    if commenters.count() > 3:
        additional = commenters.count() - 3
    else:
        additional = 0
    context = dict(**context)
    link = get_link(target, context)
    if link:
        if 'query' in link:
            link['query']['commentID'] = comment.id
        else:
            link['query'] = {'commentID': comment.id}
    return {
        'top': notification_serialize(top),
        'commenters': commenters[:3].values_list('user__username', flat=True),
        'additional': additional,
        'is_thread': is_thread,
        'display': notification_display(target),
        'link': link,
        'name': get_display_name(target, context),
    }


TYPE_MAP = {
    CHAR_TAG: char_tag,
    ORDER_UPDATE: order_update,
    SALE_UPDATE: order_update,
    SUBMISSION_CHAR_TAG: submission_char_tag,
    REVISION_UPLOADED: revision_uploaded,
    COMMENT: comment_made,
}


class EventSerializer(serializers.ModelSerializer):
    target = EventTargetRelatedField(read_only=True)
    data = SerializerMethodField(read_only=True)

    def get_data(self, obj):
        return TYPE_MAP.get(obj.type, lambda x: x.data)(obj, self.context)

    class Meta:
        model = Event
        fields = ('id', 'type', 'data', 'date', 'target')
        read_only_fields = fields


class NotificationSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ('event', 'read', 'id')
        read_only_fields = ('event', 'id')


class BulkNotificationSerializer(BulkSerializerMixin, serializers.ModelSerializer):
    event = EventSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ('event', 'read', 'id')
        read_only_fields = ('event', 'id')
        list_serializer_class = BulkListSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'name',
        )
