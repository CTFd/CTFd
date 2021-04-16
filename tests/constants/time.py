from CTFd.constants import RawEnum


class FreezeTimes(str, RawEnum):
    NOT_STARTED = "2017-10-3"  # Tuesday, October 3, 2017
    STARTED = "2017-10-5"  # Thursday, October 5, 2017
    ENDED = "2017-10-7"  # Saturday, October 7, 2017
    START = "1507089600"  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
    END = "1507262400"  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
