# Generated by Django 2.0.7 on 2018-07-25 14:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('otp_email', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TelegramDevice',
            fields=[
                ('emaildevice_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='otp_email.EmailDevice')),
            ],
            options={
                'abstract': False,
            },
            bases=('otp_email.emaildevice',),
        ),
    ]
