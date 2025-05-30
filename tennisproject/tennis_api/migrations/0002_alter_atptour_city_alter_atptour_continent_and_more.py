# Generated by Django 4.1.7 on 2024-02-08 22:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tennis_api", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="atptour",
            name="city",
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name="atptour",
            name="continent",
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name="atptour",
            name="country",
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name="atptour",
            name="currency",
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name="atptour",
            name="most_count",
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name="atptour",
            name="number_of_competitors",
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name="atptour",
            name="number_of_sets",
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name="atptour",
            name="prize_money",
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name="atptour",
            name="slug",
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name="atptour",
            name="surface",
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name="atptour",
            name="tennis_points",
            field=models.IntegerField(null=True),
        ),
    ]
