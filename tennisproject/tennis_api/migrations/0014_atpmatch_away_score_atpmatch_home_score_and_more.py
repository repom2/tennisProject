# Generated by Django 4.1.7 on 2024-03-05 20:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "tennis_api",
            "0013_wtatour_wtamatch_wtaelohard_wtaelograss_wtaeloclay_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="atpmatch",
            name="away_score",
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name="atpmatch",
            name="home_score",
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name="wtamatch",
            name="away_score",
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name="wtamatch",
            name="home_score",
            field=models.IntegerField(null=True),
        ),
    ]
