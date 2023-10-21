from .util.functions import get_stores, get_last_hour, get_last_day, get_last_week
from .util.activity_report import ActivityReport
from .util.generate_report import save_report_file
from celery import shared_task
from datetime import datetime
from .util.store import Store
import pytz


@shared_task
def trigger_report_generation(report_id: str):
    TEST_LIMIT = 3  # store count

    CURRENT_TIMESTAMP = "2023-01-25 18:13:22.47922 UTC"
    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f %Z"

    # Naive UTC Time
    parsed_time = datetime.strptime(CURRENT_TIMESTAMP, DATETIME_FORMAT)

    # Aware UTC Time
    CURRENT_TIME_UTC = pytz.utc.localize(parsed_time)

    report_data = []
    seen = set()

    last_hour_utc = get_last_hour(CURRENT_TIME_UTC)
    last_day_utc = get_last_day(CURRENT_TIME_UTC)
    last_week_utc = get_last_week(CURRENT_TIME_UTC)

    for index, store_id in enumerate(get_stores()):
        if index == TEST_LIMIT:
            break

        store_id = store_id.strip()

        if store_id in seen:
            continue

        # print(CURRENT_TIME_UTC, last_hour_utc, last_day_utc, last_week_utc)

        store = Store(store_id=store_id)
        # print("Store ID", store.id)

        store.set_timezone()
        # print("TimeZone", store.timezone)

        store.set_local_business_hours()
        # print(store.local_business_hours)

        store.set_activity_list(start_time=last_week_utc, end_time=CURRENT_TIME_UTC)
        # print("All activities in a week", store.activities)

        report = ActivityReport(store=store)

        report.calculate_uptime_downtime(
            CURRENT_TIME_UTC, last_hour_utc, last_day_utc, last_week_utc
        )

        report_data.append(report.get_result())

        seen.add(store_id)

    save_report_file(report_id=report_id, report_data=report_data)
