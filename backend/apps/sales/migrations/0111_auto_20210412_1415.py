# Generated by Django 3.1.7 on 2021-04-12 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0110_auto_20210409_1625'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transactionrecord',
            name='remote_id',
            field=models.CharField(blank=True, default='', max_length=60),
        ),
    ]
