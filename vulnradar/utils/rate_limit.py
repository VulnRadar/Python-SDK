from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Mapping

from ..constants import (
    RATE_LIMIT_HEADER,
    RATE_LIMIT_REMAINING_HEADER,
    RATE_LIMIT_RESET_HEADER,
)


@dataclass(frozen=True)
class RateLimitInfo:
    """Rate limit metadata extracted from API response headers."""

    limit: int
    used: int
    remaining: int
    resets_at: datetime | None


def parse_rate_limit_headers(headers: Mapping[str, str]) -> RateLimitInfo | None:
    """Parse rate limit information from HTTP response headers.

    Args:
        headers: HTTP response headers mapping.

    Returns:
        A RateLimitInfo instance if rate limit headers are present, otherwise None.
    """
    raw_limit = headers.get(RATE_LIMIT_HEADER)
    raw_remaining = headers.get(RATE_LIMIT_REMAINING_HEADER)
    raw_reset = headers.get(RATE_LIMIT_RESET_HEADER)

    if raw_limit is None and raw_remaining is None:
        return None

    limit = int(raw_limit) if raw_limit is not None else 0
    remaining = int(raw_remaining) if raw_remaining is not None else 0
    used = limit - remaining

    resets_at: datetime | None = None
    if raw_reset is not None:
        try:
            resets_at = datetime.fromtimestamp(int(raw_reset), tz=timezone.utc)
        except (ValueError, OSError):
            pass

    return RateLimitInfo(
        limit=limit,
        used=used,
        remaining=remaining,
        resets_at=resets_at,
    )
