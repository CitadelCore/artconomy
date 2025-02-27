# Generated by Django 2.2.1 on 2019-06-11 15:20

from django.db import migrations


def set_artist_mode(apps, schema):
    User = apps.get_model('profiles', 'User')
    User.objects.filter(products__isnull=False).update(artist_mode=True)


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0080_user_artist_mode'),
        ('sales', '0048_auto_20190610_1837'),
    ]

    operations = [
        migrations.RunPython(set_artist_mode, reverse_code=lambda x, y: None)
    ]
