# Generated by Django 2.0.4 on 2018-06-12 20:23

import apps.profiles.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0041_auto_20180605_1846'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='landscape_enabled',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='landscape_paid_through',
            field=models.DateField(blank=True, db_index=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='portrait_enabled',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='portrait_paid_through',
            field=models.DateField(blank=True, db_index=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='tg_chat_id',
            field=models.CharField(db_index=True, default='', max_length=30),
        ),
        migrations.AddField(
            model_name='user',
            name='tg_key',
            field=models.CharField(db_index=True, default=apps.profiles.models.tg_key_gen, max_length=30),
        ),
    ]
