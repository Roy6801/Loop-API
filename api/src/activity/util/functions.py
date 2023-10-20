from activity.models import Activity, BusinessHour, TimeZone
from datetime import datetime, timedelta
from typing import Generator, Any
import uuid


def generate_unique_report_id():
    return str(uuid.uuid4())


def get_stores() -> Generator[str, Any, None]:
    field = "store_id"

    store_ids_activity = Activity.objects.values_list(field, flat=True).distinct()
    store_ids_business_hours = BusinessHour.objects.values_list(
        field, flat=True
    ).distinct()
    store_ids_timezones = TimeZone.objects.values_list(field, flat=True).distinct()

    def combined_store_ids():
        for store_id in store_ids_timezones:
            yield store_id
        for store_id in store_ids_business_hours:
            yield store_id
        for store_id in store_ids_activity:
            yield store_id

    return combined_store_ids()


def get_local_time(utc_time: datetime, timezone):
    return utc_time.astimezone(timezone)


def get_last_hour(input_datetime: datetime):
    # Calculate the datetime for the last hour
    last_hour = input_datetime - timedelta(hours=1)

    return last_hour


def get_last_day(input_datetime: datetime):
    # Calculate the datetime for the last day
    last_day = input_datetime - timedelta(days=1)

    return last_day


def get_last_week(input_datetime: datetime):
    # Calculate the datetime for the last week
    last_week = input_datetime - timedelta(weeks=1)

    return last_week
