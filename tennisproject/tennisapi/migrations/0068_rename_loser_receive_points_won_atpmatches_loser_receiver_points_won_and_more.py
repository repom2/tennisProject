# Generated by Django 4.1.7 on 2024-08-02 10:31

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("tennisapi", "0067_atpmatches_loser_receive_points_won_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="atpmatches",
            old_name="loser_receive_points_won",
            new_name="loser_receiver_points_won",
        ),
        migrations.RenameField(
            model_name="atpmatches",
            old_name="winner_receive_points_won",
            new_name="winner_receiver_points_won",
        ),
        migrations.RenameField(
            model_name="wtamatches",
            old_name="loser_receive_points_won",
            new_name="loser_receiver_points_won",
        ),
        migrations.RenameField(
            model_name="wtamatches",
            old_name="winner_receive_points_won",
            new_name="winner_receiver_points_won",
        ),
    ]
