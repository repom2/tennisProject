# Generated by Django 4.1.7 on 2024-03-09 08:00

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("tennisapi", "0044_match_away_score_match_home_score_and_more"),
    ]

    operations = [
        migrations.DeleteModel(
            name="AtpTourTest",
        ),
        migrations.RemoveField(
            model_name="matchrolandg",
            name="away",
        ),
        migrations.RemoveField(
            model_name="matchrolandg",
            name="home",
        ),
        migrations.RemoveField(
            model_name="matchtest",
            name="away",
        ),
        migrations.RemoveField(
            model_name="matchtest",
            name="home",
        ),
        migrations.RemoveField(
            model_name="matchtest",
            name="tour",
        ),
        migrations.DeleteModel(
            name="Tournaments",
        ),
        migrations.RemoveField(
            model_name="wtamatchrolandg",
            name="away",
        ),
        migrations.RemoveField(
            model_name="wtamatchrolandg",
            name="home",
        ),
        migrations.DeleteModel(
            name="MatchRolandG",
        ),
        migrations.DeleteModel(
            name="MatchTest",
        ),
        migrations.DeleteModel(
            name="WtaMatchRolandG",
        ),
    ]
