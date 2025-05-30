# Generated by Django 4.1.7 on 2023-03-26 10:39

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("sportscore", "0007_rename_name_translation_players_name_translations"),
    ]

    operations = [
        migrations.CreateModel(
            name="Teams",
            fields=[
                ("id", models.TextField(primary_key=True, serialize=False)),
                ("sport_id", models.TextField(null=True)),
                ("category_id", models.TextField(null=True)),
                ("venue_id", models.TextField(null=True)),
                ("manager_id", models.TextField(null=True)),
                ("slug", models.TextField(null=True)),
                ("name", models.TextField(null=True)),
                ("name_translations", models.JSONField(null=True)),
                ("logo", models.TextField(null=True)),
                ("has_logo", models.BooleanField(null=True)),
                ("name_short", models.TextField(null=True)),
                ("name_full", models.TextField(null=True)),
                ("name_code", models.TextField(null=True)),
                ("has_sub", models.BooleanField(null=True)),
                ("gender", models.TextField(null=True)),
                ("is_nationality", models.BooleanField(null=True)),
                ("country_code", models.TextField(null=True)),
                ("country", models.TextField(null=True)),
                ("flag", models.TextField(null=True)),
                ("foundation", models.TextField(null=True)),
                ("details", models.JSONField(null=True)),
            ],
        ),
    ]
