# Generated by Django 2.0.6 on 2018-06-25 15:40

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0023_auto_20180619_2130'),
    ]

    operations = [
        migrations.AddField(
            model_name='creditcardtoken',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True, db_index=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='paymentrecord',
            name='note',
            field=models.TextField(blank=True, default=''),
        ),
    ]