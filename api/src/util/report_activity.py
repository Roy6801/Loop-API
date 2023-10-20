from datetime import datetime
from .store import Store
import pytz


TIME_FORMAT = "%H:%M:%S"


class ReportActivity:
    def __init__(self, store: Store):
        self.store = store
        self.uptime_last_hour = None
        self.uptime_last_day = None
        self.uptime_last_week = None
        self.downtime_last_hour = None
        self.downtime_last_day = None
        self.downtime_last_week = None

    def calculate_uptime_downtime(
        self, monitor_start_time: datetime, monitor_end_time: datetime, activity_list
    ):
        if all(
            x is None for x in (self.store.timezone, self.store.local_business_hours)
        ):
            raise Exception(
                "Store object lacks data! Set store attributes for uptime/downtime calculation!"
            )

        monitor_start_time = monitor_start_time.astimezone(self.store.timezone)
        monitor_end_time = monitor_end_time.astimezone(self.store.timezone)

        activities = list(activity_list)
        length = len(activity_list)

        previous_weekday: int = None
        business_start_time: datetime = None
        business_end_time: datetime = None

        uptime: int = 0
        downtime: int = 0

        for index, activity in enumerate(activities):
            # print("ACTIVITY TIME", activity, activity.status, activity.timestamp_utc)
            local_datetime = activity.timestamp_utc.astimezone(self.store.timezone)

            local_week_day = local_datetime.weekday()
            local_time = local_datetime.time()

            if local_week_day != previous_weekday:
                previous_weekday = local_week_day
                business_hours = self.store.local_business_hours[local_week_day]
                business_start_time = datetime.strptime(
                    business_hours[0], TIME_FORMAT
                ).time()
                business_end_time = datetime.strptime(
                    business_hours[1], TIME_FORMAT
                ).time()

                start_time = max(monitor_start_time, business_start_time)
                end_time = min(monitor_end_time, business_end_time)

            if start_time <= local_time <= end_time:
                print(start_time, local_time, end_time)
                difference = (end_time - local_time).second
                if activity.status == "active":
                    uptime += difference
                else:
                    downtime += difference

                end_time = local_time

                # if index == length - 1:
                #     difference = (local_time - monitor_start_time).second
                #     if activity.status == "active":
                #         uptime += difference
                #     else:
                #         downtime += difference

        return uptime, downtime

    def calculate_total_uptime_downtime(
        self, current_time, last_hour, last_day, last_week
    ):
        if all(
            x is None
            for x in (
                self.store.timezone,
                self.store.local_business_hours,
                self.store.last_hour_activity,
                self.store.last_day_activity,
                self.store.last_week_activity,
            )
        ):
            raise Exception(
                "Store object lacks data! Set store attributes for total uptime/downtime calculation!"
            )

        result = self.calculate_uptime_downtime(
            monitor_start_time=current_time,
            monitor_end_time=last_hour,
            activity_list=self.store.last_hour_activity,
        )

        self.uptime_last_hour, self.downtime_last_hour = result

        result = self.calculate_uptime_downtime(
            monitor_start_time=last_day,
            monitor_end_time=last_hour,
            activity_list=self.store.last_day_activity,
        )

        self.uptime_last_day, self.downtime_last_day = result
        self.uptime_last_day += self.uptime_last_hour
        self.downtime_last_day += self.downtime_last_hour

        result = self.calculate_uptime_downtime(
            monitor_start_time=last_week,
            monitor_end_time=last_day,
            activity_list=self.store.last_week_activity,
        )

        self.uptime_last_week, self.downtime_last_week = result
        self.uptime_last_week += self.uptime_last_day
        self.downtime_last_week += self.downtime_last_day

    def get_last_hour(self):
        return self.uptime_last_hour / 60, self.downtime_last_hour / 60

    def get_last_day(self):
        return self.uptime_last_day / 3600, self.downtime_last_day / 3600

    def get_last_week(self):
        return self.uptime_last_week / 3600, self.downtime_last_week / 3600
