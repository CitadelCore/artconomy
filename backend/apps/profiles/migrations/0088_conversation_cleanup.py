# Generated by Django 2.2.1 on 2019-07-10 20:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0087_set_sender_participant'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='conversation',
            name='body',
        ),
        migrations.RemoveField(
            model_name='conversation',
            name='edited',
        ),
        migrations.RemoveField(
            model_name='conversation',
            name='edited_on',
        ),
        migrations.RemoveField(
            model_name='conversation',
            name='last_activity',
        ),
        migrations.RemoveField(
            model_name='conversation',
            name='sender',
        ),
        migrations.RemoveField(
            model_name='conversation',
            name='sender_left',
        ),
        migrations.RemoveField(
            model_name='conversation',
            name='sender_read',
        ),
        migrations.RemoveField(
            model_name='conversation',
            name='subject',
        ),
    ]