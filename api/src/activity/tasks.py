from .util.activity_report import ActivityReport
from .util.functions import get_local_time
from activity.models import Report
from celery import shared_task
from .util.store import Store
import pandas as pd


@shared_task
def process_batch(
    batch_of_stores,
    current_time_utc,
    last_hour_utc,
    last_day_utc,
    last_week_utc,
):
    report_data = []
    local_times = {}

    for store_id in batch_of_stores:
        store_id = store_id.strip()

        # print(CURRENT_TIME_UTC, last_hour_utc, last_day_utc, last_week_utc)

        store = Store(store_id=store_id)
        # print("Store ID", store.id)

        store.set_timezone()
        # print("TimeZone", store.timezone)

        store.set_local_business_hours()
        # print(store.local_business_hours)

        store.set_activity_list(start_time=last_week_utc, end_time=current_time_utc)
        # print("All activities in a week", store.activities)

        report = ActivityReport(store=store)

        timezone_str = str(store.timezone)

        if timezone_str not in local_times:
            current_time_local = get_local_time(current_time_utc, store.timezone)
            last_hour_local = get_local_time(last_hour_utc, store.timezone)
            last_day_local = get_local_time(last_day_utc, store.timezone)
            last_week_local = get_local_time(last_week_utc, store.timezone)

            local_times[timezone_str] = (
                current_time_local,
                last_hour_local,
                last_day_local,
                last_week_local,
            )

        report.calculate_uptime_downtime(*local_times[timezone_str])

        report_data.append(report.get_result())

    return report_data


@shared_task
def save_report_file(results, report_id):
    csv_file_path = f"report/{report_id}.csv"

    data = []

    for result in results:
        data.extend(result)

    df = pd.DataFrame(
        data,
        columns=[
            "store_id",
            "uptime_last_hour",
            "uptime_last_day",
            "uptime_last_week",
            "downtime_last_hour",
            "downtime_last_day",
            "downtime_last_week",
        ],
    )
    report = Report.objects.filter(report_id=report_id)

    try:
        df.to_csv(csv_file_path, index=False)
        report.update(status=Report.STATUS_COMPLETE)
    except Exception:
        report.update(status=Report.STATUS_FAILED)
