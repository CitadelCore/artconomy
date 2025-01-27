# Generated by Django 3.2.6 on 2021-09-06 18:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sales', '0119_webhookrecord_connect'),
    ]

    operations = [
        migrations.AddField(
            model_name='webhookrecord',
            name='secret',
            field=models.CharField(default='', max_length=250),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='deliverable',
            name='processor',
            field=models.CharField(choices=[('authorize', 'EVO Authorize.net'), ('stripe', 'Stripe')], db_index=True, max_length=24),
        ),
        migrations.AlterField(
            model_name='stripeaccount',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='stripe_account', to=settings.AUTH_USER_MODEL),
        ),
    ]
