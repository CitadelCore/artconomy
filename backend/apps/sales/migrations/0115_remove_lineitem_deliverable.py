# Generated by Django 3.1.7 on 2021-04-22 22:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0114_create_invoices'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lineitem',
            name='deliverable',
        ),
    ]
