# Generated by Django 4.1.7 on 2024-03-31 12:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "tennisapi",
            "0061_bet_away_ah_7_5_bet_home_ah_7_5_betwta_away_ah_7_5_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="bet",
            name="away_dr_clay",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="bet",
            name="away_matches_clay",
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name="bet",
            name="away_rpw_clay",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="bet",
            name="away_spw_clay",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="bet",
            name="home_dr_clay",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="bet",
            name="home_matches_clay",
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name="bet",
            name="home_rpw_clay",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="bet",
            name="home_spw_clay",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="bet",
            name="stats_win_clay",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="betwta",
            name="away_dr_clay",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="betwta",
            name="away_matches_clay",
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name="betwta",
            name="away_rpw_clay",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="betwta",
            name="away_spw_clay",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="betwta",
            name="home_dr_clay",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="betwta",
            name="home_matches_clay",
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name="betwta",
            name="home_rpw_clay",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="betwta",
            name="home_spw_clay",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="betwta",
            name="stats_win_clay",
            field=models.FloatField(null=True),
        ),
    ]
