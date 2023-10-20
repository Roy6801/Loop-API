from .functions import get_stores, get_last_hour, get_last_day, get_last_week
from .report_activity import ReportActivity
from datetime import datetime
from .store import Store

CURRENT_TIMESTAMP = "2023-01-25 18:13:22.47922 UTC"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f %Z"


parsed_time = datetime.strptime(CURRENT_TIMESTAMP, DATETIME_FORMAT)

CURRENT_TIME_UTC = parsed_time


def main_operation():
    seen = set()

    for store_id in get_stores():
        store_id = store_id.strip()

        if store_id in seen:
            continue

        last_hour_utc = get_last_hour(CURRENT_TIME_UTC)
        last_day_utc = get_last_day(CURRENT_TIME_UTC)
        last_week_utc = get_last_week(CURRENT_TIME_UTC)
        # print(CURRENT_TIME_UTC, last_hour_utc, last_day_utc, last_week_utc)

        store = Store(store_id=store_id)
        print("Store ID", store.id)

        store.set_timezone()
        # print("TimeZone", store.timezone)

        store.set_local_business_hours()
        # print(store.local_business_hours)

        store.set_activity_list(
            current_time=CURRENT_TIME_UTC,
            last_hour=last_hour_utc,
            last_day=last_day_utc,
            last_week=last_week_utc,
        )
        # print("Last Hour Activity", store.last_hour_activity)
        # print("Last Day Activity", store.last_day_activity)
        # print("Last Week Activity", store.last_week_activity)

        report = ReportActivity(store=store)
        report.calculate_total_uptime_downtime(
            current_time=CURRENT_TIME_UTC,
            last_hour=last_hour_utc,
            last_day=last_day_utc,
            last_week=last_week_utc,
        )
        print("last_hour", report.get_last_hour())
        print("last_day", report.get_last_day())
        print("last_week", report.get_last_week())

        seen.add(store_id)

        # for testing a single store_id
        # break
