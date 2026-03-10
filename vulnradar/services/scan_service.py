from __future__ import annotations

from ..http import HTTPClient
from ..models.scan_result import ScanResult
from ..utils.url_validation import validate_url


class ScanService:
    """Handles single-URL security scans."""

    def __init__(self, http: HTTPClient) -> None:
        self._http = http

    def scan(self, url: str) -> ScanResult:
        """Run a security scan against a single URL.

        Args:
            url: The target URL to scan. Must be a valid http/https URL.

        Returns:
            A ScanResult containing findings, summary, and metadata.

        Raises:
            InvalidURLError: If the URL is malformed.
            AuthenticationError: If the API key is invalid.
            RateLimitError: If the rate limit is exceeded.
        """
        validate_url(url)
        data = self._http.post("/scan", {"url": url})
        return ScanResult.from_dict(data)
