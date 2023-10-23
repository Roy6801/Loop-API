from datetime import datetime, _Time, _Date
from .functions import get_local_time
from activity.models import Activity
from .store import Store
from typing import Tuple
import math


ReportResult = Tuple[str, int, int, int, int, int, int]

TIME_FORMAT: str = "%H:%M:%S"


class ActivityReport:
    def __init__(self, store: Store):
        self.store = store
        self.uptime_last_hour: int = 0
        self.uptime_last_day: int = 0
        self.uptime_last_week: int = 0
        self.downtime_last_hour: int = 0
        self.downtime_last_day: int = 0
        self.downtime_last_week: int = 0

    def calculate_uptime_downtime(
        self,
        current_time_local: datetime,
        last_hour_local: datetime,
        last_day_local: datetime,
        last_week_local: datetime,
    ):
        if all(
            [x is None for x in [self.store.timezone, self.store.local_business_hours]]
        ):
            raise Exception("Missing Store Attributes!")

        checkpoint_time: _Time | None
        checkpoint_date: _Date | None
        activity: Activity

        local_datetime: datetime
        local_week_day: int
        local_time: _Time
        local_date: _Date

        business_hours: Tuple[str, str]
        business_start_time: _Time
        business_end_time: _Time

        start_time: _Time | None
        end_time: _Time | None

        checkpoint_time = None
        checkpoint_date = None
        start_time = None
        end_time = None

        for activity in self.store.activities:
            local_datetime = get_local_time(activity.timestamp_utc, self.store.timezone)
            local_week_day = local_datetime.weekday()
            local_time = local_datetime.time()
            local_date = local_datetime.date()

            if checkpoint_date != local_date:
                checkpoint_date = local_date
                business_hours = self.store.local_business_hours[local_week_day]
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

            if start_time is not None and end_time is not None:
                if start_time <= local_time <= end_time:
                    if checkpoint_time is not None:
                        difference_seconds = (
                            datetime.combine(datetime.min, checkpoint_time)
                            - datetime.combine(datetime.min, local_time)
                        ).seconds

                        if activity.status == "active":
                            self.uptime_last_week += difference_seconds

                            if local_datetime >= last_hour_local:
                                self.uptime_last_hour += difference_seconds

                            if local_datetime >= last_day_local:
                                self.uptime_last_day += difference_seconds

                        else:
                            self.downtime_last_week += difference_seconds

                            if local_datetime >= last_hour_local:
                                self.downtime_last_hour += difference_seconds

                            if local_datetime >= last_day_local:
                                self.downtime_last_day += difference_seconds

                    checkpoint_time = local_time

    def get_result(self) -> ReportResult:
        uptime_last_hour_in_mins = int(math.ceil(self.uptime_last_hour / 60))
        uptime_last_day_in_hours = int(math.ceil(self.uptime_last_day / 3600))
        uptime_last_week_in_hours = int(math.ceil(self.uptime_last_week / 3600))
        downtime_last_hour_in_mins = int(math.ceil(self.downtime_last_hour / 60))
        downtime_last_day_in_hours = int(math.ceil(self.downtime_last_day / 3600))
        downtime_last_week_in_hours = int(math.ceil(self.downtime_last_week / 3600))

        return (
            self.store.id,
            uptime_last_hour_in_mins,
            uptime_last_day_in_hours,
            uptime_last_week_in_hours,
            downtime_last_hour_in_mins,
            downtime_last_day_in_hours,
            downtime_last_week_in_hours,
        )
