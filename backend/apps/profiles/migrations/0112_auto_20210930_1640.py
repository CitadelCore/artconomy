# Generated by Django 3.2.6 on 2021-09-30 21:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0111_remove_user_processor'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='processor_override',
            field=models.CharField(blank=True, choices=[('authorize', 'EVO Authorize.net'), ('stripe', 'Stripe')], default='', max_length=24),
        ),
        migrations.AlterField(
            model_name='artistprofile',
            name='bank_account_status',
            field=models.IntegerField(blank=True, choices=[(0, 'Unset'), (1, 'In supported country'), (2, 'No supported country')], db_index=True, default=0),
        ),
    ]
