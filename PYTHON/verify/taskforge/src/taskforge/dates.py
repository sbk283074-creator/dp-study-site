"""Parse the due-date formats the CLI accepts."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta


def parse_due(value: str, *, today: date | None = None) -> datetime:
    """Accept 'today', 'tomorrow', '+3d', or YYYY-MM-DD. Returns midnight UTC."""
    text = value.strip().lower()
    today = today or date.today()

    if text == "today":
        return datetime.combine(today, time.min)
    if text == "tomorrow":
        return datetime.combine(today + timedelta(days=1), time.min)
    if text.startswith("+"):
        try:
            days = int(text[1:].removesuffix("d"))
        except ValueError:
            raise ValueError(f"cannot parse relative due date {value!r}") from None
        return datetime.combine(today + timedelta(days=days), time.min)
    try:
        return datetime.combine(date.fromisoformat(text), time.min)
    except ValueError:
        raise ValueError(
            f"cannot parse due date {value!r}; use today, tomorrow, +3d or YYYY-MM-DD"
        ) from None
