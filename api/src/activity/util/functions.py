from activity.models import Activity, Report
from datetime import datetime, timedelta
from typing import Any
import typing
import pytz
import uuid

if typing.TYPE_CHECKING:
    from django.db.models.query import ValuesQuerySet


def get_report_id() -> str:
    """
    Generates a unique report ID using UUID and saves it as a new report in the database.
    Returns:
        str: A unique report ID.
    """

    report_id = str(uuid.uuid4())
    report: Report = Report(report_id=report_id)
    report.save()
    return report_id


def get_stores(last_week_utc: datetime) -> "ValuesQuerySet[Activity, Any]":
    """
    Retrieves a list of store IDs that had activities in the last week based on a specified UTC time.
    Args:
        last_week_utc (datetime): Time one week ago in UTC.
    Returns:
        ValuesQuerySet[Activity, Any]: A queryset containing store IDs.
    """

    stores: "ValuesQuerySet[Activity, Any]" = (
        Activity.objects.filter(timestamp_utc__gt=last_week_utc)
        .values_list("store_id", flat=True)
        .distinct()
    )

    return stores


def get_local_time(utc_time: datetime, timezone: pytz.BaseTzInfo) -> datetime:
    """
    Converts a UTC time to the local time of a specified timezone and returns it as a datetime object.
    Args:
        utc_time (datetime): Time in UTC.
        timezone (pytz.BaseTzInfo): Timezone to convert to.
    Returns:
        datetime: Local time in the specified timezone.
    """

    return utc_time.astimezone(timezone)


def get_last_hour(input_datetime: datetime) -> datetime:
    """
    Calculates and returns the datetime for one hour ago from the input datetime.
    Args:
        input_datetime (datetime): The input datetime.
    Returns:
        datetime: The datetime one hour ago.
    """

    last_hour: datetime = input_datetime - timedelta(hours=1)

    return last_hour


def get_last_day(input_datetime: datetime) -> datetime:
    """
    Calculates and returns the datetime for one day ago from the input datetime.
    Args:
        input_datetime (datetime): The input datetime.
    Returns:
        datetime: The datetime one day ago.
    """

    last_day: datetime = input_datetime - timedelta(days=1)

    return last_day


def get_last_week(input_datetime: datetime) -> datetime:
    """
    Calculates and returns the datetime for one week ago from the input datetime.
    Args:
        input_datetime (datetime): The input datetime.
    Returns:
        datetime: The datetime one week ago.
    """

    last_week: datetime = input_datetime - timedelta(weeks=1)

    return last_week
