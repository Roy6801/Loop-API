# Generated by Django 4.2.6 on 2023-10-20 16:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("activity", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="report",
            name="created_time",
        ),
        migrations.RemoveField(
            model_name="report",
            name="generated_time",
        ),
        migrations.AlterField(
            model_name="report",
            name="status",
            field=models.SmallIntegerField(
                choices=[(0, "Running"), (1, "Complete"), (2, "Failed")], default=0
            ),
        ),
    ]
