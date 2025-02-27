# Generated by Django 3.0.4 on 2020-03-24 17:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import djmoney.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0097_auto_20200317_1659'),
        ('lib', '0028_genericreference'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sales', '0081_auto_20200324_1100'),
    ]

    operations = [
        migrations.AddField(
            model_name='transactionrecord',
            name='targets',
            field=models.ManyToManyField(related_name='referencing_transactions', to='lib.GenericReference'),
        ),
    ]
