# Generated by Django 3.2.13 on 2022-05-07 11:43

import apps.profiles.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0122_remove_submission_artists'),
    ]

    operations = [
        migrations.AlterField(
            model_name='artisttag',
            name='display_position',
            field=models.FloatField(db_index=True, default=apps.profiles.models.get_next_artist_position),
        ),
        migrations.AlterField(
            model_name='charactertag',
            name='display_position',
            field=models.FloatField(db_index=True, default=apps.profiles.models.get_next_character_position),
        ),
        migrations.AlterField(
            model_name='submission',
            name='display_position',
            field=models.FloatField(db_index=True, default=apps.profiles.models.get_next_submission_position),
        ),
    ]
