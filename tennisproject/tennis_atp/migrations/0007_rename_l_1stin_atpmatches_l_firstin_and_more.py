# Generated by Django 4.1.7 on 2023-06-03 19:58

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("tennis_atp", "0006_rename_l_1stin_atpmatches_l_1stin_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="atpmatches",
            old_name="l_1stin",
            new_name="l_firstin",
        ),
        migrations.RenameField(
            model_name="atpmatches",
            old_name="l_1stwon",
            new_name="l_firstwon",
        ),
        migrations.RenameField(
            model_name="atpmatches",
            old_name="l_2ndwon",
            new_name="l_secondwon",
        ),
        migrations.RenameField(
            model_name="atpmatches",
            old_name="w_1stin",
            new_name="w_firstin",
        ),
        migrations.RenameField(
            model_name="atpmatches",
            old_name="w_1stwon",
            new_name="w_firstwon",
        ),
        migrations.RenameField(
            model_name="atpmatches",
            old_name="w_2ndwon",
            new_name="w_secondwon",
        ),
    ]
