# Generated by Django 5.0.2 on 2024-03-13 17:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sustainability', '0003_leaderboard_public'),
    ]

    operations = [
        migrations.RenameField(
            model_name='leaderboard',
            old_name='public',
            new_name='is_public',
        ),
    ]