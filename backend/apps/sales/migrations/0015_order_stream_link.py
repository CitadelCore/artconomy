# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-01-02 16:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0014_auto_20171229_2114'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='stream_link',
            field=models.URLField(blank=True, default=''),
        ),
    ]