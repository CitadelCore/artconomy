# Generated by Django 2.0.4 on 2018-05-29 20:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lib', '0012_auto_20180510_1417'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='email',
            field=models.BooleanField(default=False),
        ),
    ]
