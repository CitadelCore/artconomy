# Generated by Django 2.0.8 on 2018-10-03 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0063_user_referred_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='bought_shield_on',
            field=models.DateTimeField(blank=True, db_index=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='sold_shield_on',
            field=models.DateTimeField(blank=True, db_index=True, default=None, null=True),
        ),
    ]
