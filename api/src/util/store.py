from activity.models import Activity, BusinessHour, TimeZone
from datetime import datetime
import pytz


class Store:
    def __init__(self, store_id):
        self.id = store_id
        self.timezone = None
        self.local_business_hours = None
        self.last_hour_activity = None
        self.last_day_activity = None
        self.last_week_activity = None
        self.valid_activity = None

    def set_timezone(self):
        timezone = TimeZone.objects.filter(store_id=self.id).first()

        self.timezone = (
            pytz.timezone("America/Chicago")
            if timezone is None
            else pytz.timezone(timezone.timezone_str)
        )

    def set_local_business_hours(self):
        hours = {}

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

    def get_activity_list(self, start_time: datetime, end_time: datetime):
        start_time = pytz.timezone("UTC").localize(start_time)
        end_time = pytz.timezone("UTC").localize(end_time)

        # print("START", start_time, "END", end_time)
        # print(type(start_time), type(end_time))
        return Activity.objects.filter(
            store_id=self.id, timestamp_utc__range=(start_time, end_time)
        ).order_by("timestamp_utc")

    def set_activity_list(self, current_time, last_hour, last_day, last_week):
        self.last_hour_activity = self.get_activity_list(
            start_time=last_hour, end_time=current_time
        )

        self.last_day_activity = self.get_activity_list(
            start_time=last_day, end_time=last_hour
        )

        self.last_week_activity = self.get_activity_list(
            start_time=last_week, end_time=last_day
        )
