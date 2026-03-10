from __future__ import annotations

from dataclasses import dataclass, field

from .constants import BASE_URL, DEFAULT_TIMEOUT, DEFAULT_RETRIES, DEFAULT_RETRY_BACKOFF


@dataclass
class VulnRadarConfig:
    """Configuration for the VulnRadar SDK client."""

    api_key: str
    base_url: str = field(default=BASE_URL)
    timeout: int = field(default=DEFAULT_TIMEOUT)
    retries: int = field(default=DEFAULT_RETRIES)
    retry_backoff: float = field(default=DEFAULT_RETRY_BACKOFF)
