# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-01-31 17:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0004_auto_20180131_1457'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='private',
            field=models.BooleanField(default=False),
        ),
    ]
