from .functions import get_last_hour, get_last_day, get_last_week, get_stores
from activity.tasks import process_batch, save_report_file
from datetime import datetime
from celery import chord
import pytz


def trigger_report_generation(report_id: str, batch_size=4):
    tasks = []

    CURRENT_TIMESTAMP = "2023-01-25 18:13:22.47922 UTC"
    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f %Z"

    # Naive UTC Time
    parsed_time = datetime.strptime(CURRENT_TIMESTAMP, DATETIME_FORMAT)

    # Aware UTC Time
    CURRENT_TIME_UTC = pytz.utc.localize(parsed_time)

    last_hour_utc = get_last_hour(CURRENT_TIME_UTC)
    last_day_utc = get_last_day(CURRENT_TIME_UTC)
    last_week_utc = get_last_week(CURRENT_TIME_UTC)

    stores = get_stores(last_week_utc)
    num_stores = len(stores)
    # print("NUM STORES", num_stores)

    for batch_start in range(0, num_stores, batch_size):
        batch_end = min(batch_start + batch_size, num_stores)
        batch = stores[batch_start:batch_end]
        task_sign = process_batch.s(
            batch,
            CURRENT_TIME_UTC,
            last_hour_utc,
            last_day_utc,
            last_week_utc,
        )
        tasks.append(task_sign)

    chord(tasks)(save_report_file.s(report_id))
