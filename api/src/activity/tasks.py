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
    """
    Subtask for processing report data for a single store.

    Args:
        store_id (str): Identifier of the store to process.
        current_time_utc (datetime): Current time in UTC.
        last_hour_utc (datetime): Time one hour ago in UTC.
        last_day_utc (datetime): Time 24 hours ago in UTC.
        last_week_utc (datetime): Time one week ago in UTC.

    Returns:
        ReportResult: A tuple containing report data for the store.
    """

    store: Store
    report: ActivityReport
    timezone_str: str
    result: ReportResult

    store_id = store_id.strip()

    # Create a Store instance for the store.
    store = Store(store_id=store_id)

    # Set the store's timezone.
    store.set_timezone()

    # Set the store's local business hours.
    store.set_local_business_hours()

    # Set the store's activity list within the specified time range.
    store.set_activity_list(start_time=last_week_utc, end_time=current_time_utc)

    # Create an ActivityReport instance for the store.
    report = ActivityReport(store=store)

    timezone_str = str(store.timezone)

    if cache.get(timezone_str) is None:
        # If the timezone information is not cached, calculate and cache it.
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

    # Calculate and retrieve the store's uptime and downtime.
    report.calculate_uptime_downtime(*cache.get(timezone_str))

    # Get the result containing uptime and downtime data.
    result = report.get_result()

    return result


@shared_task
def process_batch(
    batch_of_stores: List[str],
    current_time_utc: datetime,
    last_hour_utc: datetime,
    last_day_utc: datetime,
    last_week_utc: datetime,
) -> List[ReportResult]:
    """
    Task for processing a batch of stores and generating report data.

    Args:
        batch_of_stores (List[str]): List of store identifiers to process.
        current_time_utc (datetime): Current time in UTC.
        last_hour_utc (datetime): Time one hour ago in UTC.
        last_day_utc (datetime): Time 24 hours ago in UTC.
        last_week_utc (datetime): Time one week ago in UTC.

    Returns:
        List[ReportResult]: A list of report data for the batch of stores.
    """

    pool: ThreadPoolExecutor
    results: Iterator[ReportResult]
    report_data: List[ReportResult]

    report_data = []

    # Create a thread pool with workers for parallel processing.
    pool = ThreadPoolExecutor(max_workers=len(batch_of_stores))

    # Map the subtask function to the list of store IDs, performing the subtasks concurrently.
    results = pool.map(
        lambda x: subtask(*x),
        [
            (store_id, current_time_utc, last_hour_utc, last_day_utc, last_week_utc)
            for store_id in batch_of_stores
        ],
    )

    # Collect the results and store them in the report_data list.
    report_data = list(results)

    # Shut down the thread pool.
    pool.shutdown()

    return report_data


@shared_task
def save_report_file(results: List[List[ReportResult]], report_id: str) -> None:
    """
    Task for saving report data to a CSV file and updating the report status.

    Args:
        results (List[List[ReportResult]]): List of report data for multiple stores.
        report_id (str): Identifier of the report.

    Returns:
        None
    """

    csv_file_path: str
    report: BaseManager[Report]
    data: List[ReportResult]

    csv_file_path = f"report/{report_id}.csv"

    data = []

    for result in results:
        # Extend the data list with the report data for each store.
        data.extend(result)

    # Create a DataFrame from the report data.
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
        # Write the report data to a CSV file and mark the report as complete.
        df.to_csv(csv_file_path, index=False)
        report.update(status=Report.STATUS_COMPLETE)
    except Exception:
        # Mark the report as failed in case of an error.
        report.update(status=Report.STATUS_FAILED)
