# Generated by Django 3.2.13 on 2022-05-07 09:09

import apps.lib.abstract_models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import short_stuff.django.models
import short_stuff.lib


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0119_alter_user_landscape_enabled'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='landscape_enabled',
        ),
        migrations.RemoveField(
            model_name='user',
            name='landscape_paid_through',
        ),
        migrations.CreateModel(
            name='ArtistTag',
            fields=[
                ('display_position', models.FloatField(db_index=True)),
                ('hidden', models.BooleanField(db_index=True, default=False)),
                ('id', short_stuff.django.models.ShortCodeField(db_index=True, default=short_stuff.lib.gen_shortcode, primary_key=True, serialize=False)),
                ('submission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='profiles.submission')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-display_position', 'id'),
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='submission',
            name='artists_new',
            field=models.ManyToManyField(blank=True, related_name='art_new', through='profiles.ArtistTag', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='submission',
            name='display_position',
            field=models.FloatField(db_index=True, default=0),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='CharacterTag',
            fields=[
                ('display_position', models.FloatField(db_index=True)),
                ('id', short_stuff.django.models.ShortCodeField(db_index=True, default=short_stuff.lib.gen_shortcode, primary_key=True, serialize=False)),
                ('hidden', models.BooleanField(db_index=True, default=False)),
                ('reference', models.BooleanField(db_index=True, default=False)),
                ('submission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='profiles.submission')),
                ('character', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='profiles.character')),
            ],
            options={
                'ordering': ('-display_position', 'id'),
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='submission',
            name='characters_new',
            field=models.ManyToManyField(blank=True, related_name='submissions_new', through='profiles.CharacterTag', to='profiles.Character'),
        ),
    ]
