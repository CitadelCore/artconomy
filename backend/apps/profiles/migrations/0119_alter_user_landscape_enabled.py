# Generated by Django 3.2.12 on 2022-03-05 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0118_service_plan_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='landscape_enabled',
            field=models.BooleanField(db_index=True, default=False, null=True),
        ),
    ]
