# Generated by Django 2.0.8 on 2018-10-03 15:32
from django.contrib.contenttypes.models import ContentType
from django.db import migrations


REFERRAL_PORTRAIT_CREDIT = 33
REFERRAL_LANDSCAPE_CREDIT = 34


def add_referral(apps, schema):
    User = apps.get_model('profiles', 'User')
    Subscription = apps.get_model('lib', 'Subscription')
    # Remove any broken subscriptions from previous iteration.
    Subscription.objects.filter(type=REFERRAL_PORTRAIT_CREDIT).delete()
    Subscription.objects.filter(type=REFERRAL_LANDSCAPE_CREDIT).delete()
    # Need to use native model to force creation if it does not exist.
    content_type = ContentType.objects.get_for_model(User)
    for user in User.objects.all():
        Subscription.objects.get_or_create(
            subscriber=user,
            content_type_id=content_type.id,
            object_id=user.id,
            type=REFERRAL_PORTRAIT_CREDIT,
            email=True
        )
        Subscription.objects.get_or_create(
            subscriber=user,
            content_type_id=content_type.id,
            object_id=user.id,
            type=REFERRAL_LANDSCAPE_CREDIT,
            email=True
        )


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0064_auto_20181003_1501'),
    ]

    operations = [
        migrations.RunPython(add_referral)
    ]
