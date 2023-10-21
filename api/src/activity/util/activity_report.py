from .functions import get_local_time
from datetime import datetime
from .store import Store
import math


TIME_FORMAT = "%H:%M:%S"


class ActivityReport:
    def __init__(self, store: Store):
        self.store = store
        self.uptime_last_hour = 0
        self.uptime_last_day = 0
        self.uptime_last_week = 0
        self.downtime_last_hour = 0
        self.downtime_last_day = 0
        self.downtime_last_week = 0

    def calculate_uptime_downtime(
        self, current_time_local, last_hour_local, last_day_local, last_week_local
    ):
        checkpoint_time = None
        checkpoint_date = None

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

            if start_time <= local_time <= end_time:
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

    def get_result(self):
        uptime_last_hour_in_mins = math.ceil(self.uptime_last_hour / 60)
        uptime_last_day_in_hours = math.ceil(self.uptime_last_day / 3600)
        uptime_last_week_in_hours = math.ceil(self.uptime_last_week / 3600)
        downtime_last_hour_in_mins = math.ceil(self.downtime_last_hour / 60)
        downtime_last_day_in_hours = math.ceil(self.downtime_last_day / 3600)
        downtime_last_week_in_hours = math.ceil(self.downtime_last_week / 3600)

        return (
            self.store.id,
            uptime_last_hour_in_mins,
            uptime_last_day_in_hours,
            uptime_last_week_in_hours,
            downtime_last_hour_in_mins,
            downtime_last_day_in_hours,
            downtime_last_week_in_hours,
        )
