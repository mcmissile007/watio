"""
TODO
"""
import time
from datetime import datetime
import pytz


def wake_up_on_time(_hour: int, _minute: int, timezone: pytz.timezone):
    """
    TODO
    """
    while True:
        _now = datetime.now(tz=timezone)
        time_to_wake_up = _now.replace(
            hour=_hour, minute=_minute, second=0, microsecond=0
        )
        time_to_wake_up_limit = _now.replace(
            hour=_hour, minute=_minute + 5, second=0, microsecond=0
        )
        if _now > time_to_wake_up and _now < time_to_wake_up_limit:
            return
        time.sleep(30)


def wake_up_o_clock(timezone: pytz.timezone) -> datetime:
    """
    TODO
    """
    while True:
        _now = datetime.now(tz=timezone)
        if _now.minute == 0:
            return _now.replace(second=0, microsecond=0)
        time.sleep(10)
