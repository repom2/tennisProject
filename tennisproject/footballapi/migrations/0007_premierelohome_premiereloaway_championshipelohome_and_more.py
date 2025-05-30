# Generated by Django 4.1.7 on 2024-02-03 11:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("footballapi", "0006_championshipelo"),
    ]

    operations = [
        migrations.CreateModel(
            name="PremierEloHome",
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
                ("elo", models.IntegerField()),
                ("elo_change", models.IntegerField()),
                ("games", models.IntegerField()),
                ("date", models.DateField(null=True)),
                (
                    "match",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="elo_rating_home",
                        to="footballapi.premierleague",
                    ),
                ),
                (
                    "team",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="elo_rating_home",
                        to="footballapi.teams",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PremierEloAway",
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
                ("elo", models.IntegerField()),
                ("elo_change", models.IntegerField()),
                ("games", models.IntegerField()),
                ("date", models.DateField(null=True)),
                (
                    "match",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="elo_rating_away",
                        to="footballapi.premierleague",
                    ),
                ),
                (
                    "team",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="elo_rating_away",
                        to="footballapi.teams",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ChampionshipEloHome",
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
                ("elo", models.IntegerField()),
                ("elo_change", models.IntegerField()),
                ("games", models.IntegerField()),
                ("date", models.DateField(null=True)),
                (
                    "match",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="elo_rating_home",
                        to="footballapi.championship",
                    ),
                ),
                (
                    "team",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="championship_home_elo_rating",
                        to="footballapi.teams",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ChampionshipEloAway",
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
                ("elo", models.IntegerField()),
                ("elo_change", models.IntegerField()),
                ("games", models.IntegerField()),
                ("date", models.DateField(null=True)),
                (
                    "match",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="elo_rating_away",
                        to="footballapi.championship",
                    ),
                ),
                (
                    "team",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="championship_away_elo_rating",
                        to="footballapi.teams",
                    ),
                ),
            ],
        ),
    ]
