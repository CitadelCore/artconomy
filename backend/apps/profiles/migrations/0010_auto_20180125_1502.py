# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-01-25 15:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0009_character_tags'),
    ]

    database_operations = [
        migrations.AlterModelTable('Tag', 'lib_tag')
    ]

    state_operations = [
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=database_operations,
            state_operations=state_operations
        )
    ]
