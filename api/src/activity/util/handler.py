from .functions import get_last_hour, get_last_day, get_last_week, get_stores
from activity.tasks import process_batch, save_report_file
from activity.models import Activity
from celery.canvas import Signature
from datetime import datetime
from typing import Any, List
from celery import chord
import typing
import pytz

if typing.TYPE_CHECKING:
    from django.db.models.query import ValuesQuerySet


def trigger_report_generation(report_id: str, batch_size: int = 4) -> None:
    tasks: List[Signature] = []

    CURRENT_TIMESTAMP: str
    DATETIME_FORMAT: str

    parsed_time: datetime
    current_time_utc: datetime

    last_hour_utc: datetime
    last_day_utc: datetime
    last_week_utc: datetime

    stores: "ValuesQuerySet[Activity, Any]"
    num_stores: int

    batch_start: int
    batch_end: int
    batch: "ValuesQuerySet[Activity, Any]"

    task_sign: Signature

    CURRENT_TIMESTAMP = "2023-01-25 18:13:22.47922 UTC"
    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f %Z"

    # Naive UTC Time
    parsed_time = datetime.strptime(CURRENT_TIMESTAMP, DATETIME_FORMAT)

    # Aware UTC Time
    current_time_utc = pytz.utc.localize(parsed_time)

    last_hour_utc = get_last_hour(current_time_utc)
    last_day_utc = get_last_day(current_time_utc)
    last_week_utc = get_last_week(current_time_utc)

    stores = get_stores(last_week_utc)
    num_stores = len(stores)
    # print("NUM STORES", num_stores)

    for batch_start in range(0, num_stores, batch_size):
        batch_end = min(batch_start + batch_size, num_stores)
        batch = stores[batch_start:batch_end]
        task_sign = process_batch.s(
            batch,
            current_time_utc,
            last_hour_utc,
            last_day_utc,
            last_week_utc,
        )
        tasks.append(task_sign)

    chord(tasks)(save_report_file.s(report_id))
