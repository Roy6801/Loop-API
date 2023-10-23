from concurrent.futures import ThreadPoolExecutor
from .util.activity_report import ActivityReport
from django.db.models.manager import BaseManager
from .util.functions import get_local_time
from typing import Iterator, List, Tuple
from django.core.cache import cache
from activity.models import Report
from celery import shared_task
from .util.store import Store
from datetime import datetime
import pandas as pd

ReportResult = Tuple[str, int, int, int, int, int, int]


def subtask(
    store_id: str,
    current_time_utc: datetime,
    last_hour_utc: datetime,
    last_day_utc: datetime,
    last_week_utc: datetime,
) -> ReportResult:
    """"""

    store: Store
    report: ActivityReport
    timezone_str: str
    result: ReportResult

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

    if cache.get(timezone_str) is None:
        current_time_local = get_local_time(current_time_utc, store.timezone)
        last_hour_local = get_local_time(last_hour_utc, store.timezone)
        last_day_local = get_local_time(last_day_utc, store.timezone)
        last_week_local = get_local_time(last_week_utc, store.timezone)

        cache.set(
            timezone_str,
            (
                current_time_local,
                last_hour_local,
                last_day_local,
                last_week_local,
            ),
        )

    report.calculate_uptime_downtime(*cache.get(timezone_str))

    result = report.get_result()

    return result


@shared_task
def process_batch(
    batch_of_stores: List[str],
    current_time_utc: datetime,
    last_hour_utc: datetime,
    last_day_utc: datetime,
    last_week_utc: datetime,
) -> Iterator[ReportResult]:
    """"""

    report_data: List[ReportResult]
    pool: ThreadPoolExecutor
    result: ReportResult
    results: Iterator[ReportResult]

    report_data = []
    pool = ThreadPoolExecutor(max_workers=len(batch_of_stores))

    results = pool.map(
        lambda x: subtask(*x),
        [
            (store_id, current_time_utc, last_hour_utc, last_day_utc, last_week_utc)
            for store_id in batch_of_stores
        ],
    )

    # for result in results:
    #     report_data.append(result)

    pool.shutdown()

    return results


@shared_task
def save_report_file(results: Iterator[ReportResult], report_id: str):
    csv_file_path: str
    report: BaseManager[Report]
    data: List[ReportResult]

    csv_file_path = f"report/{report_id}.csv"

    data = []

    # for result in results:
    #     data.extend(result)

    df = pd.DataFrame(
        results,
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
