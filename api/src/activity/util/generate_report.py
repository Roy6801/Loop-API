from activity.models import Report
import pandas as pd
import uuid


def get_report_id():
    report_id = str(uuid.uuid4())
    report = Report(report_id=report_id)
    report.save()
    return report_id


def save_report_file(report_id, report_data, dirpath="./report"):
    df = pd.DataFrame(
        report_data,
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
        df.to_csv(f"{dirpath}/{report_id}.csv", index=False)
        report.update(status=Report.STATUS_COMPLETE)
    except Exception:
        report.update(status=Report.STATUS_FAILED)


def fetch_report_file(report_id, dirpath="./report"):
    pass
