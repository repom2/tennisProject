# Generated by Django 4.1.7 on 2024-02-03 08:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("footballapi", "0004_championship"),
    ]

    operations = [
        migrations.CreateModel(
            name="Teams",
            fields=[
                ("id", models.TextField(primary_key=True, serialize=False)),
                ("name", models.TextField(null=True)),
                ("name_short", models.TextField(null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name="championship",
            name="away_team_id",
        ),
        migrations.RemoveField(
            model_name="championship",
            name="home_team_id",
        ),
        migrations.RemoveField(
            model_name="premierleague",
            name="away_team_id",
        ),
        migrations.RemoveField(
            model_name="premierleague",
            name="home_team_id",
        ),
        migrations.AlterField(
            model_name="championship",
            name="start_at",
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.CreateModel(
            name="PremierElo",
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
                        related_name="elo_rating",
                        to="footballapi.premierleague",
                    ),
                ),
                (
                    "team",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="elo_rating",
                        to="footballapi.teams",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="championship",
            name="away_team",
            field=models.ForeignKey(
                default="",
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="away_championship_matches",
                to="footballapi.teams",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="championship",
            name="home_team",
            field=models.ForeignKey(
                default="",
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="home_championship_matches",
                to="footballapi.teams",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="premierleague",
            name="away_team",
            field=models.ForeignKey(
                default="",
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="away_matches",
                to="footballapi.teams",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="premierleague",
            name="home_team",
            field=models.ForeignKey(
                default="",
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="home_matches",
                to="footballapi.teams",
            ),
            preserve_default=False,
        ),
    ]
