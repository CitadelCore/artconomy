# Generated by Django 3.2.8 on 2021-11-02 21:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0112_auto_20210930_1640'),
    ]

    operations = [
        migrations.AddField(
            model_name='artistprofile',
            name='public_queue',
            field=models.BooleanField(default=False, help_text='Allow people to see your queue.'),
        ),
    ]