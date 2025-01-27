# Generated by Django 2.2.10 on 2020-02-24 18:57

from django.db import migrations, models
import django.db.models.deletion
import djmoney.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0079_auto_20200220_0849'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='payout',
        ),
        migrations.RemoveField(
            model_name='product',
            name='payout_currency',
        ),
        migrations.AlterField(
            model_name='product',
            name='base_price',
            field=djmoney.models.fields.MoneyField(db_index=True, decimal_places=2, default_currency='USD', max_digits=6, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='file',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='full_sales_product', to='lib.Asset'),
        ),
        migrations.AlterField(
            model_name='revision',
            name='file',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='full_sales_revision', to='lib.Asset'),
        ),
    ]
