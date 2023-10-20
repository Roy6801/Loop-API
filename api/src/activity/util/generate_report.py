from .functions import generate_unique_report_id
from activity.models import Report
import pandas as pd


class GenerateReport:
    def __init__(self) -> None:
        self.__data = []
        self.__report_id = generate_unique_report_id()

    def add_store_activity_report(self, report_data):
        self.__data.append(report_data)

    def save_report_file(self, dirpath="./report"):
        df = pd.DataFrame(
            self.__data,
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

        df.to_csv(f"{dirpath}/{self.__report_id}.csv", index=False)

    def get_report_id(self):
        report = Report(report_id=self.__report_id)
        report.save()
        return self.__report_id
