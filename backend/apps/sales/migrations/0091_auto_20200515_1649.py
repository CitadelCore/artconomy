# Generated by Django 3.0.6 on 2020-05-15 21:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import short_stuff.django.models
import short_stuff.lib


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('lib', '0029_auto_20200324_1542'),
        ('sales', '0090_auto_20200315_1128'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliverable',
            name='name',
            field=models.CharField(default='', max_length=150),
        ),
        migrations.AlterField(
            model_name='deliverable',
            name='arbitrator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cases', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='order',
            name='claim_token',
            field=short_stuff.django.models.ShortCodeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='transactionrecord',
            name='category',
            field=models.IntegerField(choices=[(400, 'Artconomy Service Fee'), (401, 'Escrow hold'), (402, 'Escrow release'), (403, 'Escrow refund'), (404, 'Subscription dues'), (405, 'Refund for subscription dues'), (406, 'Cash withdrawal'), (408, 'Third party fee'), (409, 'Premium service bonus'), (410, 'Internal Transfer'), (411, 'Third party refund'), (412, 'Correction'), (413, 'Table Service'), (414, 'Tax'), (416, 'Manual Payout')], db_index=True),
        ),
        migrations.AlterField(
            model_name='transactionrecord',
            name='id',
            field=short_stuff.django.models.ShortCodeField(db_index=True, default=short_stuff.lib.gen_shortcode, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='transactionrecord',
            name='targets',
            field=models.ManyToManyField(blank=True, related_name='referencing_transactions', to='lib.GenericReference'),
        ),
    ]
