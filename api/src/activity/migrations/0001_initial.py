# Generated by Django 4.2.6 on 2023-10-20 06:47

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Activity",
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
                ("store_id", models.CharField(max_length=255)),
                (
                    "status",
                    models.CharField(
                        choices=[("active", "ACTIVE"), ("inactive", "INACTIVE")],
                        default="active",
                        max_length=10,
                    ),
                ),
                ("timestamp_utc", models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name="BusinessHour",
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
                ("store_id", models.CharField(max_length=255)),
                (
                    "day_of_week",
                    models.SmallIntegerField(
                        choices=[
                            (0, "Mon"),
                            (1, "Tue"),
                            (2, "Wed"),
                            (3, "Thu"),
                            (4, "Fri"),
                            (5, "Sat"),
                            (6, "Sun"),
                        ],
                        db_index=True,
                    ),
                ),
                ("start_time_local", models.CharField(max_length=255)),
                ("end_time_local", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="Report",
            fields=[
                (
                    "report_id",
                    models.CharField(max_length=255, primary_key=True, serialize=False),
                ),
                (
                    "status",
                    models.SmallIntegerField(
                        choices=[(0, "Running"), (1, "Complete")], default=0
                    ),
                ),
                ("created_time", models.DateTimeField(auto_now_add=True)),
                ("generated_time", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="TimeZone",
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
                ("store_id", models.CharField(max_length=255)),
                ("timezone_str", models.CharField(max_length=255)),
            ],
        ),
    ]
