from datetime import datetime, date, time
from .functions import get_local_time
from activity.models import Activity
from .store import Store
from typing import Tuple
import math


ReportResult = Tuple[str, int, int, int, int, int, int]

TIME_FORMAT: str = "%H:%M:%S"


class ActivityReport:
    """
    Represents a report generated for a store and calculates uptime and downtime.
    """

    def __init__(self, store: Store):
        """
        Initializes a new ActivityReport instance for a given store.
        Args:
            store (Store): The store for which the report is generated.
        """

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
        """
        Calculates uptime and downtime for the store based on its activities within a given time frame.
        Args:
            current_time_local (datetime): Current time in the store's local timezone.
            last_hour_local (datetime): Time one hour ago in the store's local timezone.
            last_day_local (datetime): Time 24 hours ago in the store's local timezone.
            last_week_local (datetime): Time one week ago in the store's local timezone.
        """

        if all(
            [x is None for x in [self.store.timezone, self.store.local_business_hours]]
        ):
            raise Exception("Missing Store Attributes!")

        checkpoint_time: time | None
        checkpoint_date: date | None
        activity: Activity

        local_datetime: datetime
        local_week_day: int
        local_time: time
        local_date: date

        business_hours: Tuple[str, str]
        business_start_time: time
        business_end_time: time

        start_time: time | None
        end_time: time | None

        checkpoint_time = None
        checkpoint_date = None
        start_time = None
        end_time = None

        for activity in self.store.activities:
            # Convert activity timestamp to the local timezone

            local_datetime = get_local_time(activity.timestamp_utc, self.store.timezone)
            local_week_day = local_datetime.weekday()
            local_time = local_datetime.time()
            local_date = local_datetime.date()

            # Check if the date has changed to handle different business hours
            if checkpoint_date != local_date:
                checkpoint_date = local_date
                business_hours = self.store.local_business_hours[local_week_day]
                business_start_time = datetime.strptime(
                    business_hours[0], "%H:%M:%S"
                ).time()
                business_end_time = datetime.strptime(
                    business_hours[1], "%H:%M:%S"
                ).time()

                # Determine the start and end times for the current date
                if local_date == last_week_local.date():
                    # If within the last week, consider the maximum of the last week's time and business start time
                    start_time = max(last_week_local.time(), business_start_time)
                else:
                    start_time = business_start_time

                if local_date == current_time_local.date():
                    # If within the current day, consider the minimum of the current day's time and business end time
                    end_time = min(current_time_local.time(), business_end_time)
                else:
                    end_time = business_end_time

                checkpoint_time = end_time

            # Check if the activity is within the calculated time range
            if start_time is not None and end_time is not None:
                if start_time <= local_time <= end_time:
                    if checkpoint_time is not None:
                        # Calculate the time difference in seconds between checkpoints
                        difference_seconds = (
                            datetime.combine(datetime.min, checkpoint_time)
                            - datetime.combine(datetime.min, local_time)
                        ).seconds

                        # If the activity is 'active', accumulate uptime time
                        if activity.status == "active":
                            self.uptime_last_week += difference_seconds

                            if local_datetime >= last_hour_local:
                                # If within the last hour, accumulate uptime for the last hour
                                self.uptime_last_hour += difference_seconds

                            if local_datetime >= last_day_local:
                                # If within the last day, accumulate uptime for the last day
                                self.uptime_last_day += difference_seconds

                        else:
                            # If the activity is not 'active', accumulate downtime time
                            self.downtime_last_week += difference_seconds

                            if local_datetime >= last_hour_local:
                                # If within the last hour, accumulate downtime for the last hour
                                self.downtime_last_hour += difference_seconds

                            if local_datetime >= last_day_local:
                                # If within the last day, accumulate downtime for the last day
                                self.downtime_last_day += difference_seconds

                    checkpoint_time = local_time

    def get_result(self) -> ReportResult:
        """
        Returns the calculated uptime and downtime in minutes and hours as a tuple.
        Returns:
            ReportResult: A tuple containing store ID, uptime, and downtime values.
        """

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
