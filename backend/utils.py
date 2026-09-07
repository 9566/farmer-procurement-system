from datetime import datetime, timezone, timedelta


IST = timezone(timedelta(hours=5, minutes=30))


def today_ist():
    """Return today's date according to Indian Standard Time."""
    return datetime.now(IST).date()


def now_utc():
    """Return current UTC datetime without timezone information."""
    return datetime.now(timezone.utc).replace(tzinfo=None)