# Generated by Django 3.0.11 on 2020-12-30 16:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0104_add_catalog'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='file_old',
        ),
        migrations.RemoveField(
            model_name='product',
            name='preview_old',
        ),
        migrations.RemoveField(
            model_name='reference',
            name='file_old',
        ),
        migrations.RemoveField(
            model_name='reference',
            name='preview_old',
        ),
        migrations.RemoveField(
            model_name='revision',
            name='file_old',
        ),
        migrations.RemoveField(
            model_name='revision',
            name='preview_old',
        ),
    ]
