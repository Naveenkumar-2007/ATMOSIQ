from datetime import UTC, datetime, timedelta


def now_utc():
    return datetime.now(UTC)


def floor_hour(dt):
    return dt.replace(minute=0, second=0, microsecond=0)


def lead_time_hours(issue_time, valid_time):
    return (valid_time - issue_time) / timedelta(hours=1)


def resolve_date(value):
    v = str(value).strip().lower()
    if v == "yesterday":
        return (now_utc() - timedelta(days=1)).strftime("%Y-%m-%d")
    if v == "today":
        return now_utc().strftime("%Y-%m-%d")
    return str(value)
