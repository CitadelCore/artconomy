# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-01-17 19:51
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0003_auto_20180117_1948'),
    ]

    operations = [
        migrations.RenameField(
            model_name='imageasset',
            old_name='artist',
            new_name='artists',
        ),
    ]
