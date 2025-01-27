# Generated by Django 2.2.10 on 2020-02-20 00:45

from decimal import Decimal
from django.db import migrations, models
import django.db.models.deletion
import djmoney.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0076_auto_20200218_1819'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='track_inventory',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AlterField(
            model_name='lineitem',
            name='amount',
            field=djmoney.models.fields.MoneyField(blank=True, decimal_places=2, default=Decimal('0'), default_currency='USD', max_digits=6),
        ),
        migrations.AlterField(
            model_name='lineitem',
            name='destination_account',
            field=models.IntegerField(choices=[(300, 'Credit Card'), (301, 'Bank Account'), (302, 'Escrow'), (303, 'Finalized Earnings, available for withdraw'), (304, 'Contingency reserve'), (305, 'Unannotated earnings'), (306, 'Card transaction fees'), (307, 'Other card fees'), (308, 'ACH Transaction fees'), (309, 'Other ACH fees'), (310, 'Tax staging'), (311, 'Tax')]),
        ),
        migrations.AlterField(
            model_name='transactionrecord',
            name='category',
            field=models.IntegerField(choices=[(400, 'Artconomy Service Fee'), (401, 'Escrow hold'), (402, 'Escrow release'), (403, 'Escrow refund'), (404, 'Subscription dues'), (405, 'Refund for subscription dues'), (406, 'Cash withdrawal'), (407, 'Cash deposit'), (408, 'Third party fee'), (409, 'Premium service bonus'), (410, 'Internal Transfer'), (411, 'Third party refund'), (412, 'Correction'), (414, 'Tax')], db_index=True),
        ),
        migrations.AlterField(
            model_name='transactionrecord',
            name='destination',
            field=models.IntegerField(choices=[(300, 'Credit Card'), (301, 'Bank Account'), (302, 'Escrow'), (303, 'Finalized Earnings, available for withdraw'), (304, 'Contingency reserve'), (305, 'Unannotated earnings'), (306, 'Card transaction fees'), (307, 'Other card fees'), (308, 'ACH Transaction fees'), (309, 'Other ACH fees'), (310, 'Tax staging'), (311, 'Tax')], db_index=True),
        ),
        migrations.AlterField(
            model_name='transactionrecord',
            name='source',
            field=models.IntegerField(choices=[(300, 'Credit Card'), (301, 'Bank Account'), (302, 'Escrow'), (303, 'Finalized Earnings, available for withdraw'), (304, 'Contingency reserve'), (305, 'Unannotated earnings'), (306, 'Card transaction fees'), (307, 'Other card fees'), (308, 'ACH Transaction fees'), (309, 'Other ACH fees'), (310, 'Tax staging'), (311, 'Tax')], db_index=True),
        ),
        migrations.CreateModel(
            name='InventoryTracker',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.IntegerField(db_index=True, default=0)),
                ('product', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='sales.Product')),
            ],
        ),
    ]
