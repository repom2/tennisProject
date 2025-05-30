# Generated by Django 4.1.7 on 2025-02-06 10:37

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tennisapi", "0072_bet_stats_win_hard_betwta_stats_win_hard"),
    ]

    operations = [
        migrations.AddField(
            model_name="bet",
            name="away_elo_clay",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="bet",
            name="away_elo_clay_games",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="bet",
            name="away_elo_grass",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="bet",
            name="away_elo_grass_games",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="bet",
            name="away_elo_hard",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="bet",
            name="away_elo_hard_games",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="bet",
            name="home_elo_clay",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="bet",
            name="home_elo_clay_games",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="bet",
            name="home_elo_grass",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="bet",
            name="home_elo_grass_games",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="bet",
            name="home_elo_hard",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="bet",
            name="home_elo_hard_games",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="betwta",
            name="away_elo_clay",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="betwta",
            name="away_elo_clay_games",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="betwta",
            name="away_elo_grass",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="betwta",
            name="away_elo_grass_games",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="betwta",
            name="away_elo_hard",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="betwta",
            name="away_elo_hard_games",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="betwta",
            name="home_elo_clay",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="betwta",
            name="home_elo_clay_games",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="betwta",
            name="home_elo_grass",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="betwta",
            name="home_elo_grass_games",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="betwta",
            name="home_elo_hard",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="betwta",
            name="home_elo_hard_games",
            field=models.FloatField(null=True),
        ),
    ]
