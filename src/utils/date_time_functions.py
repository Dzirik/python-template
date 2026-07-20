"""
Functions for helping with date and/or time manipulation within the project.
"""

from datetime import datetime

from numpy.random import default_rng

# Create a random number generator instance
_rng = default_rng()


def convert_datetime_to_string_date(now: datetime | None = None, add_micro: bool = False, sep: str = "-") -> str:
    """
    Converts now to string format yyyy-mm-dd-hh-mm-ss<-micro>.
    :param now: datetime. Date in datetime format. Default value is datetime.now().
    :param add_micro: bool. If to add microseconds too.
    :param sep: str. Separator in between time data. Default is "-".
    :return: str.
    """
    if now is None:
        now = datetime.now()
    now_str = (
        f"{now.year}{sep}{now.month:02d}{sep}{now.day:02d}{sep}{now.hour:02d}{sep}{now.minute:02d}{sep}{now.second:02d}"
    )
    if add_micro:
        now_str = f"{now_str}{sep}{now.microsecond:06d}"
    return now_str


def create_datetime_id(now: datetime | None = None, add_micro: bool = False) -> str:
    """
    Creates date time id in the form yyyy-mm-dd-hh-mm-ss<-micro>_xxx where xxx is randomly generated integer.
    :param now: datetime. Date in datetime format. Default value is datetime.now().
    :param add_micro: bool. If to add microseconds too.
    :return: str.
    """
    if now is None:
        now = datetime.now()
    return f"{convert_datetime_to_string_date(now, add_micro)}_{int(_rng.integers(0, 999)):03d}"


def create_date_id(now: datetime | None = None) -> str:
    """
    Creates date id in the form yyyy-mm-dd_xxx where xxx is randomly generated integer.
    :param now: datetime. Date in datetime format. Default value is datetime.now().
    :return: str.
    """
    if now is None:
        now = datetime.now()
    return f"{now.year}-{now.month:02d}-{now.day:02d}_{int(_rng.integers(0, 999)):03d}"


def convert_string_date_to_datetime(now_str: str, sep: str = "-", add_micro: bool = False) -> datetime:
    """
    Converts string of the format yyyy-mm-dd-hh-mm-ss<-micro> to datetime format.
    :param now_str: str. String of the format yyyy-mm-dd-hh-mm-ss<-micro>, produced with the same
     sep and add_micro used here.
    :param sep: str. Separator in between time data, matching the one used to build now_str. Default is "-".
    :param add_micro: bool. If now_str carries a trailing microseconds field to parse.
    :return: datetime.
    """
    fmt_fields = ["%Y", "%m", "%d", "%H", "%M", "%S"]
    if add_micro:
        fmt_fields.append("%f")
    fmt = sep.join(fmt_fields)
    return datetime.strptime(now_str, fmt)


if __name__ == "__main__":
    d = datetime.now()
    print(convert_datetime_to_string_date(d, False))
    print(convert_datetime_to_string_date(d, True))
    print(create_datetime_id(d))
    print(create_date_id(d))
    print(convert_string_date_to_datetime(convert_datetime_to_string_date(d, False)))
