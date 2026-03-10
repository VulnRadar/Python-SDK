from __future__ import annotations

from ..http import HTTPClient
from ..models.crawl import DiscoveryResult
from ..utils.url_validation import validate_url


class DiscoveryService:
    """Discovers crawlable URLs for a given target domain."""

    def __init__(self, http: HTTPClient) -> None:
        self._http = http

    def discover_urls(self, url: str) -> DiscoveryResult:
        """Discover all crawlable URLs for a target.

        Args:
            url: The root URL to run discovery on.

        Returns:
            A DiscoveryResult with a list of discovered URLs and their count.

        Raises:
            InvalidURLError: If the URL is malformed.
            AuthenticationError: If the API key is invalid.
        """
        validate_url(url)
        data = self._http.post("/scan/crawl/discover", {"url": url})
        return DiscoveryResult.from_dict(data)
