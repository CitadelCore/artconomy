# Generated by Django 2.2.1 on 2019-11-29 22:54
from django.contrib.contenttypes.models import ContentType
from django.db import migrations, models


def set_last_activity(apps, schema):
    Comment = apps.get_model('lib', 'Comment')
    Conversation = apps.get_model('profiles', 'Conversation')
    content_type_id = ContentType.objects.get_for_model(Conversation).id
    for conversation in Conversation.objects.all():
        last_comment = Comment.objects.filter(
            object_id=conversation.id, content_type_id=content_type_id,
        ).exclude(deleted=True).order_by('-created_on').first()
        if not last_comment:
            conversation.last_activity = None
        else:
            conversation.last_activity = last_comment.created_on
        conversation.save()


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0093_auto_20191119_1645'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversation',
            name='last_activity',
            field=models.DateTimeField(db_index=True, default=None, null=True),
        ),
        migrations.RunPython(
            set_last_activity, reverse_code=lambda x, y: None,
        )
    ]
