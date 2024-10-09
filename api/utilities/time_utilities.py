from datetime import datetime, tzinfo

from pytz import timezone


def change_timezone_to_london(dt: datetime):
    return change_time_zone(dt, timezone('Europe/London'))


def change_time_zone(dt: datetime, tz: tzinfo):
    return dt.astimezone(tz)
