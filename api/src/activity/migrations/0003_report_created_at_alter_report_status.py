# Generated by Django 4.2.6 on 2023-10-21 13:58

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("activity", "0002_remove_report_created_time_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="report",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="report",
            name="status",
            field=models.SmallIntegerField(
                choices=[
                    ("Running", "Running"),
                    ("Complete", "Complete"),
                    ("Failed", "Failed"),
                ],
                default="Running",
            ),
        ),
    ]