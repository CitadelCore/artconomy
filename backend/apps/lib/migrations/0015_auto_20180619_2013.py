# Generated by Django 2.0.4 on 2018-06-19 20:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lib', '0014_auto_20180529_2025'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='telegram',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AddField(
            model_name='subscription',
            name='until',
            field=models.DateField(db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='email',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
