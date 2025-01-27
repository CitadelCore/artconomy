# Generated by Django 2.1.5 on 2019-05-16 22:37

from django.db import migrations


def update_notifications(apps, schema):
    Event = apps.get_model('lib', 'Event')
    for event in Event.objects.filter(data__has_key='asset'):
        event.data['submission'] = event.data.pop('asset')
        event.save()


def undo_update_notifications(apps, schema):
    Event = apps.get_model('lib', 'Event')
    for event in Event.objects.filter(data__has_key='submission'):
        event.data['asset'] = event.data.pop('submission')
        event.save()


class Migration(migrations.Migration):

    dependencies = [
        ('lib', '0021_asset'),
        ('profiles', '0075_auto_20190516_2201')
    ]

    operations = [
        migrations.RunPython(update_notifications, reverse_code=undo_update_notifications)
    ]
