# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-01-03 19:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0017_auto_20180102_2215'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ['created_on']},
        ),
        migrations.RenameField(
            model_name='order',
            old_name='placed_on',
            new_name='created_on',
        ),
        migrations.AlterField(
            model_name='paymentrecord',
            name='payment_type',
            field=models.IntegerField(choices=[(200, 'Sale of good or service'), (203, 'Internal Transfer'), (201, 'Disbursement to account'), (202, 'Refund')], db_index=True),
        ),
        migrations.AlterField(
            model_name='paymentrecord',
            name='source',
            field=models.IntegerField(choices=[(100, 'Credit Card'), (101, 'Bank Transfer'), (102, 'Escrow Holdings'), (103, 'Cash Holdings')], db_index=True),
        ),
    ]
