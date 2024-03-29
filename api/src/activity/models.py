from django.db import models

# Create your models here.


# Business Timezones Listed
class TimeZone(models.Model):
    store_id = models.CharField(max_length=255)
    timezone_str = models.CharField(max_length=255)


# Business Uptime and Downtime Records
class Activity(models.Model):
    STATUS_CHOICES = [
        ((STATUS_ACTIVE := "active"), "ACTIVE"),
        ((STATUS_INACTIVE := "inactive"), "INACTIVE"),
    ]

    store_id = models.CharField(max_length=255)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=STATUS_ACTIVE
    )
    timestamp_utc = models.DateTimeField()


# Business Hours from Monday (0) to Sunday (6)
class BusinessHour(models.Model):
    WEEK_DAY_CHOICES = [
        ((MONDAY := 0), "Mon"),
        ((TUESDAY := 1), "Tue"),
        ((WEDNESDAY := 2), "Wed"),
        ((THURSDAY := 3), "Thu"),
        ((FRIDAY := 4), "Fri"),
        ((SATURDAY := 5), "Sat"),
        ((SUNDAY := 6), "Sun"),
    ]

    store_id = models.CharField(max_length=255)
    day_of_week = models.SmallIntegerField(choices=WEEK_DAY_CHOICES, db_index=True)
    start_time_local = models.CharField(max_length=255)
    end_time_local = models.CharField(max_length=255)


# Report Tracking
class Report(models.Model):
    STATUS_CHOICES = [
        ((STATUS_RUNNING := "Running"), "Running"),
        ((STATUS_COMPLETE := "Complete"), "Complete"),
        ((STATUS_FAILED := "Failed"), "Failed"),
    ]

    report_id = models.CharField(max_length=255, primary_key=True)
    status = models.CharField(
        max_length=8, choices=STATUS_CHOICES, default=STATUS_RUNNING
    )
    created_at = models.DateTimeField(auto_now_add=True)
