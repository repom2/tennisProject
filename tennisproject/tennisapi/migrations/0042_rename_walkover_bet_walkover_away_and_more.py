# Generated by Django 4.1.7 on 2024-01-21 08:35

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tennisapi", "0041_betwta"),
    ]

    operations = [
        migrations.RenameField(
            model_name="bet",
            old_name="walkover",
            new_name="walkover_away",
        ),
        migrations.RenameField(
            model_name="betwta",
            old_name="walkover",
            new_name="walkover_away",
        ),
        migrations.AddField(
            model_name="bet",
            name="walkover_home",
            field=models.BooleanField(null=True),
        ),
        migrations.AddField(
            model_name="betwta",
            name="walkover_home",
            field=models.BooleanField(null=True),
        ),
    ]
