# Generated by Django 2.2.1 on 2020-01-16 20:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0068_auto_20200115_1510'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='table_order',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AlterField(
            model_name='order',
            name='tax_rate',
            field=models.DecimalField(decimal_places=5, default=0, help_text='Percent rate of tax to apply', max_digits=7),
        ),
        migrations.AlterField(
            model_name='product',
            name='tax_rate',
            field=models.DecimalField(decimal_places=5, default=0, help_text='Percent rate of tax to apply', max_digits=7),
        ),
    ]
