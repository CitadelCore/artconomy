# Generated by Django 2.0.6 on 2018-06-21 15:10

from django.db import migrations


def slash_fixer(apps, schema):
    Character = apps.get_model('profiles', 'Character')
    # There's a possibility for a collision here, but very remote. Will ignore and fix if it arrives.
    for char in ['/', '\\', '?', '#', '&']:
        for character in Character.objects.filter(name__contains=char):
            character.name = character.name.replace(char, '|')
            character.save()


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0042_auto_20180612_2023'),
    ]

    operations = [
        migrations.RunPython(slash_fixer, reverse_code=lambda x, y: None)
    ]
