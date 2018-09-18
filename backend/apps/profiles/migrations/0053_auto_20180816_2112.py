# Generated by Django 2.0.7 on 2018-08-16 21:12
from django.contrib.contenttypes.models import ContentType
from django.db import migrations

from apps.lib.models import TRANSFER_FAILED


def add_transfer_failed(apps, schema):
    User = apps.get_model('profiles', 'User')
    Subscription = apps.get_model('lib', 'Subscription')
    # Remove any broken subscriptions from previous iteration.
    Subscription.objects.filter(type=TRANSFER_FAILED).delete()
    # Need to use native model to force creation if it does not exist.
    content_type = ContentType.objects.get_for_model(User)
    for user in User.objects.all():
        Subscription.objects.get_or_create(
            subscriber=user,
            content_type_id=content_type.id,
            object_id=user.id,
            type=TRANSFER_FAILED,
            email=True
        )


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0052_user_auto_withdraw'),
    ]

    operations = [
        migrations.RunPython(add_transfer_failed, reverse_code=lambda x, y: None)
    ]
