# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2017-12-19 22:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lib', '0006_auto_20171219_2223'),
        ('profiles', '0005_auto_20171218_1734'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='notifications',
            field=models.ManyToManyField(through='lib.Notification', to='lib.Event'),
        ),
    ]
