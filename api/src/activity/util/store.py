from activity.models import Activity, BusinessHour, TimeZone
import pytz


class Store:
    def __init__(self, store_id):
        self.id = store_id
        self.timezone = None
        self.local_business_hours = None
        self.activities = None

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

    def set_activity_list(self, start_time, end_time):
        self.activities = (
            Activity.objects.filter(
                store_id=self.id, timestamp_utc__range=(start_time, end_time)
            )
            .order_by("timestamp_utc")
            .reverse()
        )
