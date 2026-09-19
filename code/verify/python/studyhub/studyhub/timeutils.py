from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

UTC = timezone.utc


def utcnow() -> datetime:
    """Naive UTC timestamp. Every DateTime column in this app stores this."""
    return datetime.now(UTC).replace(tzinfo=None)


def local_day(moment: datetime, tz_name: str = "UTC") -> str:
    """The user's calendar day (YYYY-MM-DD) for a UTC timestamp."""
    aware = moment.replace(tzinfo=UTC)
    return aware.astimezone(ZoneInfo(tz_name)).date().isoformat()


def end_of_local_day(moment: datetime, tz_name: str) -> datetime:
    """UTC instant corresponding to 23:59:59.999999 in the user's timezone."""
    local = moment.replace(tzinfo=UTC).astimezone(ZoneInfo(tz_name))
    midnight_tomorrow = (local + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    return midnight_tomorrow.astimezone(UTC).replace(tzinfo=None)


def last_n_days(today: str, count: int) -> list[str]:
    end = date.fromisoformat(today)
    return [(end - timedelta(days=offset)).isoformat() for offset in range(count - 1, -1, -1)]
