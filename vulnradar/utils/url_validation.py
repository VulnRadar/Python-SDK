from __future__ import annotations

import re
from urllib.parse import urlparse

from ..exceptions import InvalidURLError

_DOMAIN_RE = re.compile(
    r"^(?:[a-zA-Z0-9]"
    r"(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"
    r"\.)+[a-zA-Z]{2,}$"
)


def validate_url(url: str) -> str:
    """Validate that a URL is a well-formed http/https URL with a valid domain.

    Args:
        url: The URL string to validate.

    Returns:
        The original URL if validation passes.

    Raises:
        InvalidURLError: If the URL is malformed or uses an unsupported scheme.
    """
    try:
        parsed = urlparse(url)
    except ValueError:
        raise InvalidURLError(url)

    if parsed.scheme not in ("http", "https"):
        raise InvalidURLError(url)

    host = parsed.hostname or ""
    if not host:
        raise InvalidURLError(url)

    if not _DOMAIN_RE.match(host) and not _is_valid_ip(host):
        raise InvalidURLError(url)

    return url


def _is_valid_ip(host: str) -> bool:
    import ipaddress

    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False
