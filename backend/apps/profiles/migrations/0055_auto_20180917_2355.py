# Generated by Django 2.0.8 on 2018-09-17 23:55
from django.contrib.contenttypes.models import ContentType
from django.db import migrations

from apps.lib.models import SUBMISSION_ARTIST_TAG


def add_tag_artist(apps, schema):
    User = apps.get_model('profiles', 'User')
    ImageAsset = apps.get_model('profiles', 'ImageAsset')
    Subscription = apps.get_model('lib', 'Subscription')
    # Remove any broken subscriptions from previous iteration.
    Subscription.objects.filter(type=SUBMISSION_ARTIST_TAG).delete()
    # Need to use native model to force creation if it does not exist.
    content_type = ContentType.objects.get_for_model(ImageAsset)
    for asset in ImageAsset.objects.all():
        Subscription.objects.get_or_create(
            subscriber=asset.owner,
            content_type_id=content_type.id,
            object_id=asset.id,
            type=SUBMISSION_ARTIST_TAG,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0054_user_escrow_disabled'),
    ]

    operations = [
        migrations.RunPython(add_tag_artist, reverse_code=lambda x, y: None)
    ]
