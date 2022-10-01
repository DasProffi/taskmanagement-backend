from datetime import datetime

time_format: str = '%Y-%m-%d %H:%M:%S'


def json_timestring_to_datetime(json_string: str) -> datetime:
    tmp: datetime = datetime.strptime(json_string, time_format)
    return tmp


def datetime_to_json_timestring(date: datetime) -> str:
    return date.strftime(time_format).strip()
