# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-01-18 15:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lib', '0007_auto_20180116_1602'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='type',
            field=models.IntegerField(choices=[(0, 'New Submission'), (1, 'New Follower'), (2, 'Character Transfer Request'), (3, 'Character Tagged'), (4, 'New Comment'), (5, 'New Character'), (7, 'Commission Slots Available'), (6, 'New Product'), (11, 'New Auction'), (18, 'Update'), (19, 'Sale Update'), (15, 'Dispute Filed'), (16, 'Refund Processed'), (8, 'New Submission of Character'), (9, 'New Portfolio Item'), (14, 'New Favorite'), (10, 'Submission Tagged'), (17, 'Submission tagged with Character'), (20, 'Tagged as the artist of a submission'), (21, 'Tagged the artist of a submission'), (12, 'Announcement'), (13, 'System-wide announcement')], db_index=True),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='type',
            field=models.IntegerField(choices=[(0, 'New Submission'), (1, 'New Follower'), (2, 'Character Transfer Request'), (3, 'Character Tagged'), (4, 'New Comment'), (5, 'New Character'), (7, 'Commission Slots Available'), (6, 'New Product'), (11, 'New Auction'), (18, 'Update'), (19, 'Sale Update'), (15, 'Dispute Filed'), (16, 'Refund Processed'), (8, 'New Submission of Character'), (9, 'New Portfolio Item'), (14, 'New Favorite'), (10, 'Submission Tagged'), (17, 'Submission tagged with Character'), (20, 'Tagged as the artist of a submission'), (21, 'Tagged the artist of a submission'), (12, 'Announcement'), (13, 'System-wide announcement')], db_index=True),
        ),
    ]
