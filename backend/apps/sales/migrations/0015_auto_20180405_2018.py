# Generated by Django 2.0.3 on 2018-04-05 20:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0014_auto_20180405_2014'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owned_sales_product', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='revision',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owned_sales_revision', to=settings.AUTH_USER_MODEL),
        ),
    ]
