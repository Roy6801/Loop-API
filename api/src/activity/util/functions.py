from activity.models import Activity, Report
from datetime import datetime, timedelta
from typing import Any
import typing
import pytz
import uuid

if typing.TYPE_CHECKING:
    from django.db.models.query import ValuesQuerySet


def get_report_id() -> str:
    report_id = str(uuid.uuid4())
    report: Report = Report(report_id=report_id)
    report.save()
    return report_id


def get_stores(last_week_utc: datetime) -> "ValuesQuerySet[Activity, Any]":
    stores: "ValuesQuerySet[Activity, Any]" = (
        Activity.objects.filter(timestamp_utc__gt=last_week_utc)
        .values_list("store_id", flat=True)
        .distinct()
    )

    return stores


def get_local_time(utc_time: datetime, timezone: pytz.BaseTzInfo) -> datetime:
    return utc_time.astimezone(timezone)


def get_last_hour(input_datetime: datetime) -> datetime:
    # Calculate the datetime for the last hour
    last_hour: datetime = input_datetime - timedelta(hours=1)

    return last_hour


def get_last_day(input_datetime: datetime) -> datetime:
    # Calculate the datetime for the last day
    last_day: datetime = input_datetime - timedelta(days=1)

    return last_day


def get_last_week(input_datetime: datetime) -> datetime:
    # Calculate the datetime for the last week
    last_week: datetime = input_datetime - timedelta(weeks=1)

    return last_week
