# Generated by Django 2.2.1 on 2019-06-03 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0075_auto_20190516_2201'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='authorize_token',
            field=models.CharField(db_index=True, default='', max_length=50),
        ),
    ]
