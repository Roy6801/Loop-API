from activity.models import Activity, BusinessHour, TimeZone
from django.db.models.manager import BaseManager
from typing import Dict, Tuple
from datetime import datetime
import pytz


class Store:
    """
    Represents a store entity and provides methods to set its attributes.
    """

    def __init__(self, store_id: str):
        """
        Initializes a new Store instance.
        Args:
            store_id (str): Identifier of the store.
        """

        self.id: str = store_id
        self.timezone: pytz.BaseTzInfo
        self.local_business_hours: Dict[int, Tuple[str, str]]
        self.activities: BaseManager[Activity]

    def set_timezone(self):
        """
        Sets the store's timezone based on the database or defaults to "America/Chicago."
        """

        timezone_obj = TimeZone.objects.filter(store_id=self.id).first()

        self.timezone = (
            pytz.timezone("America/Chicago")
            if timezone_obj is None
            else pytz.timezone(timezone_obj.timezone_str)
        )

    def set_local_business_hours(self):
        """
        Retrieves and sets the store's local business hours for each day.
        """

        hours: Dict[int, Tuple[str, str]] = {}
        business_hour: BusinessHour | None
        day: int

        for day in range(7):
            business_hour = BusinessHour.objects.filter(
                store_id=self.id, day_of_week=day
            ).first()

            if business_hour is None:
                hours[day] = ("00:00:00", "23:59:59")
            else:
                hours[day] = (
                    business_hour.start_time_local,
                    business_hour.end_time_local,
                )

        self.local_business_hours = hours

    def set_activity_list(self, start_time: datetime, end_time: datetime):
        """
        Retrieves and sets the store's activities within a specified time range.
        Args:
            start_time (datetime): Start of the time range.
            end_time (datetime): End of the time range.
        """

        self.activities = (
            Activity.objects.filter(
                store_id=self.id, timestamp_utc__range=(start_time, end_time)
            )
            .order_by("timestamp_utc")
            .reverse()
        )
