# Generated by Django 4.1.7 on 2024-02-17 07:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("footballapi", "0013_bundesliga_ligue1_ligue1elohome_ligue1eloaway_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="BetFootball",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("object_id", models.TextField()),
                ("home_name", models.TextField(null=True)),
                ("away_name", models.TextField(null=True)),
                ("home_odds", models.FloatField(null=True)),
                ("draw_odds", models.FloatField(null=True)),
                ("away_odds", models.FloatField(null=True)),
                ("home_elo", models.FloatField(null=True)),
                ("away_elo", models.FloatField(null=True)),
                ("elo_home", models.FloatField(null=True)),
                ("elo_away", models.FloatField(null=True)),
                ("elo_prob", models.FloatField(null=True)),
                ("elo_prob_home", models.FloatField(null=True)),
                ("preview", models.TextField(null=True)),
                ("reasoning", models.TextField(null=True)),
                ("start_at", models.DateTimeField(null=True)),
                ("home_prob", models.FloatField(null=True)),
                ("draw_prob", models.FloatField(null=True)),
                ("away_prob", models.FloatField(null=True)),
                ("home_yield", models.FloatField(null=True)),
                ("draw_yield", models.FloatField(null=True)),
                ("away_yield", models.FloatField(null=True)),
                (
                    "away",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="away_bet",
                        to="footballapi.teams",
                    ),
                ),
                (
                    "content_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.contenttype",
                    ),
                ),
                (
                    "home",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="home_bet",
                        to="footballapi.teams",
                    ),
                ),
            ],
        ),
    ]
