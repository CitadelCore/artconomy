# Generated by Django 2.2.10 on 2020-02-19 00:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0074_auto_20200218_1449'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='tax_rate',
        ),
    ]
