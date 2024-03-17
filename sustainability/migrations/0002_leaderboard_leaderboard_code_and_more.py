# Generated by Django 5.0.2 on 2024-03-13 16:30

import sustainability.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sustainability', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='leaderboard',
            name='leaderboard_code',
            field=models.CharField(default=sustainability.models.generate_leaderboard_code, editable=False, max_length=6, unique=True),
        ),
        migrations.AlterField(
            model_name='plantoftheday',
            name='date',
            field=models.DateField(auto_now=True),
        ),
    ]