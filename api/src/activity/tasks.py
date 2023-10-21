from .util.activity_report import ActivityReport
from .util.generate_report import save_report_file
from .util.functions import *
from celery import shared_task
from datetime import datetime
from .util.store import Store
import pytz


@shared_task
def trigger_report_generation(report_id: str):
    # TEST_LIMIT = 3  # store count

    CURRENT_TIMESTAMP = "2023-01-25 18:13:22.47922 UTC"
    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f %Z"

    # Naive UTC Time
    parsed_time = datetime.strptime(CURRENT_TIMESTAMP, DATETIME_FORMAT)

    # Aware UTC Time
    CURRENT_TIME_UTC = pytz.utc.localize(parsed_time)

    report_data = []
    seen = set()

    local_times = {}

    last_hour_utc = get_last_hour(CURRENT_TIME_UTC)
    last_day_utc = get_last_day(CURRENT_TIME_UTC)
    last_week_utc = get_last_week(CURRENT_TIME_UTC)

    for index, store_id in enumerate(get_stores()):
        # if index == TEST_LIMIT:
        #     break

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

        timezone_str = str(store.timezone)

        if timezone_str not in local_times:
            current_time_local = get_local_time(CURRENT_TIME_UTC, store.timezone)
            last_hour_local = get_local_time(last_hour_utc, store.timezone)
            last_day_local = get_local_time(last_day_utc, store.timezone)
            last_week_local = get_local_time(last_week_utc, store.timezone)

            local_times[timezone_str] = (
                current_time_local,
                last_hour_local,
                last_day_local,
                last_week_local,
            )

        report.calculate_uptime_downtime(**local_times[timezone_str])

        report_data.append(report.get_result())

        seen.add(store_id)

        print("PROCESSED:", index, "Store ID -", store_id, end="\r")

    save_report_file(report_id=report_id, report_data=report_data)
