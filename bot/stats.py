"""In-memory deletion stats, keyed by (chat_id, date)."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timezone


# (chat_id, iso_date_str) -> count of deleted service messages
_counts: dict[tuple[int, str], int] = defaultdict(int)


def record_deletion(chat_id: int, n: int = 1) -> None:
    """Increment today's deletion counter for *chat_id*."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    _counts[(chat_id, today)] += n


def get_today_count(chat_id: int) -> int:
    """Return how many service messages were deleted today (UTC)."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return _counts.get((chat_id, today), 0)


def get_count_for_date(chat_id: int, d: date) -> int:
    """Return deletions for a specific date."""
    return _counts.get((chat_id, d.isoformat()), 0)

