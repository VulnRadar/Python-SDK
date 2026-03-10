from __future__ import annotations

from ..http import HTTPClient
from ..models.crawl import CrawlResult
from ..utils.url_validation import validate_url


class CrawlService:
    """Handles deep crawl scanning across multiple pages of a target."""

    def __init__(self, http: HTTPClient) -> None:
        self._http = http

    def scan_crawl(self, url: str, urls: list[str] | None = None) -> CrawlResult:
        """Run a deep crawl scan on a target URL.

        Args:
            url: The root URL to crawl and scan.
            urls: Optional list of additional URLs to include in the crawl.

        Returns:
            A CrawlResult containing per-page findings and aggregate crawl info.

        Raises:
            InvalidURLError: If any URL is malformed.
            AuthenticationError: If the API key is invalid.
            RateLimitError: If the rate limit is exceeded.
        """
        validate_url(url)
        payload: dict = {"url": url}
        if urls is not None:
            payload["urls"] = urls
        data = self._http.post("/scan/crawl", payload)
        return CrawlResult.from_dict(data)
