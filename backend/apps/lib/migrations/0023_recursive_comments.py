# Generated by Django 2.2.1 on 2019-06-26 07:03
from django.contrib.contenttypes.models import ContentType
from django.db import migrations
from django.db.models import F


def recurse_comments(apps, schema):
    Comment = apps.get_model('lib.Comment')
    content_type = ContentType.objects.get_for_model(Comment)
    Comment.objects.filter(parent__isnull=False).update(content_type_id=content_type.id, object_id=F('parent_id'))


class Migration(migrations.Migration):

    dependencies = [
        ('lib', '0022_auto_20190516_2237'),
    ]

    operations = [
        migrations.RunPython(recurse_comments, reverse_code=lambda x, y: None)
    ]