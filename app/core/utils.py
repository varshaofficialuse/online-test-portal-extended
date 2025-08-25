# app/core/utils.py
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))  # India Standard Time

def utc_now() -> datetime:
    """Return current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)

def now_ist() -> datetime:
    """Return current IST time (timezone-aware)."""
    return utc_now().astimezone(IST)

def ist_to_utc(dt: datetime) -> datetime:
    """Convert IST datetime (naive or aware) to UTC."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=IST)
    return dt.astimezone(timezone.utc)

def utc_to_ist(dt: datetime) -> datetime:
    """Convert UTC datetime to IST."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(IST)
