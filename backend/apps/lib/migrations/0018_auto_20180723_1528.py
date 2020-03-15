# Generated by Django 2.0.7 on 2018-07-23 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lib', '0017_auto_20180719_1406'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='type',
            field=models.IntegerField(choices=[(0, 'New Character'), (1, 'New Watcher'), (2, 'Character Transfer Request'), (3, 'Character Tagged'), (4, 'New Comment'), (7, 'Commission Slots Available'), (6, 'New Product'), (11, 'New Auction'), (18, 'Update'), (22, 'Revision Uploaded'), (19, 'Sale Update'), (15, 'Dispute Filed'), (16, 'Refund Processed'), (8, 'New Submission of Character'), (14, 'New Favorite'), (10, 'Submission Tagged'), (17, 'Submission tagged with Character'), (20, 'Tagged as the artist of a submission'), (21, 'Tagged the artist of a submission'), (12, 'Announcement'), (13, 'System-wide announcement'), (27, 'Renewal Failure'), (28, 'Subscription Deactivated'), (30, 'New Journal Posted'), (31, 'Token Issued')], db_index=True),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='type',
            field=models.IntegerField(choices=[(0, 'New Character'), (1, 'New Watcher'), (2, 'Character Transfer Request'), (3, 'Character Tagged'), (4, 'New Comment'), (7, 'Commission Slots Available'), (6, 'New Product'), (11, 'New Auction'), (18, 'Update'), (22, 'Revision Uploaded'), (19, 'Sale Update'), (15, 'Dispute Filed'), (16, 'Refund Processed'), (8, 'New Submission of Character'), (14, 'New Favorite'), (10, 'Submission Tagged'), (17, 'Submission tagged with Character'), (20, 'Tagged as the artist of a submission'), (21, 'Tagged the artist of a submission'), (12, 'Announcement'), (13, 'System-wide announcement'), (27, 'Renewal Failure'), (28, 'Subscription Deactivated'), (30, 'New Journal Posted'), (31, 'Token Issued')], db_index=True),
        ),
    ]
