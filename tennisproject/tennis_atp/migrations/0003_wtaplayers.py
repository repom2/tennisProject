# Generated by Django 4.1.7 on 2023-05-16 14:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tennis_atp", "0002_atpmatches"),
    ]

    operations = [
        migrations.CreateModel(
            name="WTAPlayers",
            fields=[
                ("player_id", models.TextField(primary_key=True, serialize=False)),
                ("name_first", models.TextField(null=True)),
                ("name_last", models.TextField(null=True)),
                ("hand", models.TextField(null=True)),
                ("dob", models.TextField(null=True)),
                ("ioc", models.TextField(null=True)),
                ("height", models.TextField(null=True)),
                ("wikidata_id", models.TextField(null=True)),
            ],
        ),
    ]
