# Generated by Django 2.0.4 on 2018-05-23 14:44

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0039_auto_20180521_2202'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='reset_token',
            field=models.CharField(blank=True, default='', max_length=36),
        ),
        migrations.AddField(
            model_name='user',
            name='token_expiry',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]