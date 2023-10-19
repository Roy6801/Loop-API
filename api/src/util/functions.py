from activity.models import Activity, BusinessHour, TimeZone
from datetime import datetime, timedelta
import pytz


DAY_NUM = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6,
}

CURRENT_TIMESTAMP = "2023-01-25 18:13:22.47922 UTC"
UTC_FORMAT = "%Y-%m-%d %H:%M:%S.%f %Z"
TIME_FORMAT = "%H:%M:S"

CURRENT_TIME_UTC = datetime.strptime(CURRENT_TIMESTAMP, UTC_FORMAT)


def get_stores():
    field = "store_id"

    store_ids_activity = Activity.objects.values_list(field, flat=True).distinct()
    store_ids_business_hours = BusinessHour.objects.values_list(
        field, flat=True
    ).distinct()
    store_ids_timezones = TimeZone.objects.values_list(field, flat=True).distinct()

    def combined_store_ids():
        for store_id in store_ids_timezones:
            yield store_id
        for store_id in store_ids_business_hours:
            yield store_id
        for store_id in store_ids_activity:
            yield store_id

    return combined_store_ids()


def get_local_time(utc_time, local_timezone):
    local_time = utc_time.replace(tzinfo=pytz.UTC).astimezone(local_timezone)

    return local_time


def get_last_hour(input_datetime):
    # Calculate the datetime for the last hour
    last_hour = input_datetime - timedelta(hours=1)

    return last_hour


def get_last_day(input_datetime):
    # Calculate the datetime for the last day
    last_day = input_datetime - timedelta(days=1)

    return last_day


def get_last_week(input_datetime):
    # Calculate the datetime for the last week
    last_week = input_datetime - timedelta(weeks=1)

    return last_week


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
        timezone_string = TimeZone.objects.filter(store_id=self.id).first()

        self.timezone = (
            pytz.timezone("America/Chicago")
            if timezone_string is None
            else timezone_string
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

    def get_activity_list(self, start_time, end_time):
        return Activity.objects.filter(
            store_id=self.id, timestamp_utc__range=(start_time, end_time)
        )

    def set_activity_list(self, current_time, last_hour, last_day, last_week):
        self.last_hour_activity = self.get_activity_list(
            start_time_utc=last_hour, end_time_utc=current_time
        )

        self.last_day_activity = self.get_activity_list(
            start_time_utc=last_day, end_time_utc=current_time
        )

        self.last_week_activity = self.get_activity_list(
            start_time_utc=last_week, end_time_utc=current_time
        )


class ReportActivity:
    def __init__(self, store: Store):
        self.store = store
        self.last_hour_activity = None
        self.last_day_activity = None
        self.last_week_activity = None
        self.uptime_last_hour = None
        self.uptime_last_day = None
        self.uptime_last_week = None
        self.downtime_last_hour = None
        self.downtime_last_day = None
        self.downtime_last_week = None

    def get_valid_activity_list(self, activity_list):
        valid_activity_list = []

        for activity in activity_list:
            local_time = get_local_time(activity.timestamp_utc, self.store.timezone)

            day_of_week = DAY_NUM[local_time.strftime("%A")]
            activity_time = local_time.strptime(TIME_FORMAT)

            b_hrs = self.store.local_business_hours[day_of_week]
            b_start = datetime.strptime(b_hrs[0], TIME_FORMAT)
            b_end = datetime.strptime(b_hrs[1], TIME_FORMAT)

            if b_start <= activity_time <= b_end:
                valid_activity_list.append(activity)

        return valid_activity_list

    def filter_valid_activity(self):
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
                "Store object lacks data! Set store attributes for filter operation!"
            )

        self.last_hour_activity = self.get_valid_activity_list(
            activity_list=self.store.last_hour_activity
        )

        self.last_day_activity = self.get_valid_activity_list(
            activity_list=self.store.last_day_activity
        )

        self.last_week_activity = self.get_valid_activity_list(
            activity_list=self.store.last_week_activity
        )

    def calculate_uptime(self):
        pass

    def calculate_downtime(self):
        pass


def main_operation():
    seen = set()

    for store_id in get_stores():
        if store_id in seen:
            continue

        last_hour_utc = get_last_hour(CURRENT_TIME_UTC)
        last_day_utc = get_last_day(CURRENT_TIME_UTC)
        last_week_utc = get_last_week(CURRENT_TIME_UTC)

        seen.add(store_id)
