import time
from datetime import datetime, timezone
from typing import Union

from CTFd.utils import get_config


def ctftime():
    """Checks whether it's CTF time or not."""

    start = get_config("start")
    end = get_config("end")

    if start:
        start = int(start)
    else:
        start = 0
    if end:
        end = int(end)
    else:
        end = 0

    if start and end:
        if start < time.time() < end:
            # Within the two time bounds
            return True

    if start < time.time() and end == 0:
        # CTF starts on a date but never ends
        return True

    if start == 0 and time.time() < end:
        # CTF started but ends at a date
        return True

    if start == 0 and end == 0:
        # CTF has no time requirements
        return True

    return False


def ctf_paused():
    return bool(get_config("paused"))


def ctf_started():
    return time.time() > int(get_config("start") or 0)


def ctf_ended():
    if int(get_config("end") or 0):
        return time.time() > int(get_config("end") or 0)
    return False


def view_after_ctf():
    return get_config("view_after_ctf")


def unix_time(dt: datetime) -> int:
    if dt is None or not isinstance(dt, datetime):
        print("Invalid datetime object for time filter function.")
        return None
    return int((dt - datetime(1970, 1, 1)).total_seconds())


def unix_time_millis(dt: datetime) -> int:
    ut = unix_time(dt)
    if ut is None:
        return None
    return ut * 1000


def unix_time_to_utc(t: Union[int, float]) -> datetime:
    if t is None:
        print("Invalid datetime object for time filter function.")
        return None
    return datetime.fromtimestamp(t, tz=timezone.utc)


def isoformat(dt: datetime) -> str:
    if dt is None or not isinstance(dt, datetime):
        print("Invalid datetime object for time filter function.")
        return None
    return dt.isoformat() + "Z"
