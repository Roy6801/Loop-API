from .functions import get_stores, get_last_hour, get_last_day, get_last_week
from .report_activity import ReportActivity
from datetime import datetime
from .store import Store
import pytz
import time

CURRENT_TIMESTAMP = "2023-01-25 18:13:22.47922 UTC"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f %Z"

# Naive UTC Time
parsed_time = datetime.strptime(CURRENT_TIMESTAMP, DATETIME_FORMAT)

# Aware UTC Time
CURRENT_TIME_UTC = pytz.utc.localize(parsed_time)


def main_operation():
    seen = set()

    for store_id in get_stores():
        store_id = store_id.strip()

        if store_id in seen:
            continue

        last_hour_utc = get_last_hour(CURRENT_TIME_UTC)
        last_day_utc = get_last_day(CURRENT_TIME_UTC)
        last_week_utc = get_last_week(CURRENT_TIME_UTC)
        print(CURRENT_TIME_UTC, last_hour_utc, last_day_utc, last_week_utc)

        store = Store(store_id=store_id)
        print("Store ID", store.id)

        store.set_timezone()
        print("TimeZone", store.timezone)

        store.set_local_business_hours()
        print(store.local_business_hours)

        store.set_activity_list(start_time=last_week_utc, end_time=CURRENT_TIME_UTC)
        # print("All activities in a week", store.activities)

        last_hour_local = last_hour_utc.astimezone(store.timezone)
        last_day_local = last_day_utc.astimezone(store.timezone)
        last_week_local = last_week_utc.astimezone(store.timezone)
        current_time_local = CURRENT_TIME_UTC.astimezone(store.timezone)

        checkpoint_time = None
        checkpoint_date = None

        uptime_last_hour = 0
        uptime_last_day = 0
        uptime_last_week = 0
        downtime_last_hour = 0
        downtime_last_day = 0
        downtime_last_week = 0

        for activity in store.activities:
            local_datetime = activity.timestamp_utc.astimezone(store.timezone)
            local_week_day = local_datetime.weekday()
            local_time = local_datetime.time()
            local_date = local_datetime.date()

            print(
                "CHECKPOINT",
                checkpoint_date,
                checkpoint_time,
                activity.timestamp_utc,
                local_datetime,
            )

            if checkpoint_date != local_date:
                checkpoint_date = local_date
                business_hours = store.local_business_hours[local_week_day]
                business_start_time = datetime.strptime(
                    business_hours[0], "%H:%M:%S"
                ).time()
                business_end_time = datetime.strptime(
                    business_hours[1], "%H:%M:%S"
                ).time()

                if local_date == last_week_local.date():
                    start_time = max(last_week_local.time(), business_start_time)
                else:
                    start_time = business_start_time

                if local_date == current_time_local.date():
                    end_time = min(current_time_local.time(), business_end_time)
                else:
                    end_time = business_end_time

                checkpoint_time = end_time

            if start_time <= local_time <= end_time:
                difference_seconds = (
                    datetime.combine(datetime.min, checkpoint_time)
                    - datetime.combine(datetime.min, local_time)
                ).seconds

                print(activity.status.upper(), end="\t")

                if activity.status == "active":
                    uptime_last_week += difference_seconds

                    if local_datetime >= last_hour_local:
                        uptime_last_hour += difference_seconds
                        print("HOUR", local_datetime, end="\t")

                    if local_datetime >= last_day_local:
                        uptime_last_day += difference_seconds
                        print("DAY", local_datetime, end="\t")

                    print("WEEK", local_datetime)
                else:
                    downtime_last_week += difference_seconds

                    if local_datetime >= last_hour_local:
                        downtime_last_hour += difference_seconds
                        print("HOUR", local_datetime, end="\t")

                    if local_datetime >= last_day_local:
                        downtime_last_day += difference_seconds
                        print("DAY", local_datetime, end="\t")

                    print("WEEK", local_datetime)

                checkpoint_time = local_time

        print(uptime_last_hour / 60, uptime_last_day / 3600, uptime_last_week / 3600)
        print(
            downtime_last_hour / 60,
            downtime_last_day / 3600,
            downtime_last_week / 3600,
        )

        # report = ReportActivity(store=store)
        # report.calculate_total_uptime_downtime(
        #     current_time=CURRENT_TIME_UTC,
        #     last_hour=last_hour_utc,
        #     last_day=last_day_utc,
        #     last_week=last_week_utc,
        # )
        # print("last_hour", report.get_last_hour())
        # print("last_day", report.get_last_day())
        # print("last_week", report.get_last_week())

        seen.add(store_id)

        # for testing a single store_id
        # break
        time.sleep(5)
