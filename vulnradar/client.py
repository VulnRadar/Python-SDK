from __future__ import annotations

from typing import Any

from .config import VulnRadarConfig
from .constants import BASE_URL, DEFAULT_TIMEOUT, DEFAULT_RETRIES
from .http import HTTPClient
from .models.scan_result import ScanResult
from .models.crawl import CrawlResult, DiscoveryResult
from .models.version import VersionInfo
from .services.scan_service import ScanService
from .services.history_service import HistoryService
from .services.crawl_service import CrawlService
from .services.discovery_service import DiscoveryService
from .services.metadata_service import MetadataService


class VulnRadar:
    """The main VulnRadar SDK client.

    Provides access to all VulnRadar API capabilities through a clean,
    typed interface.

    Args:
        api_key: Your VulnRadar API key.
        base_url: Override the default API base URL.
        timeout: HTTP request timeout in seconds. Default: 30.
        retries: Number of retry attempts for transient server errors. Default: 3.

    Example:
        >>> from vulnradar import VulnRadar
        >>> client = VulnRadar(api_key="your-api-key")
        >>> result = client.scan("https://example.com")
        >>> print(result.summary.total)
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = BASE_URL,
        timeout: int = DEFAULT_TIMEOUT,
        retries: int = DEFAULT_RETRIES,
    ) -> None:
        self._config = VulnRadarConfig(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            retries=retries,
        )
        self._http = HTTPClient(self._config)

        self._scan_service = ScanService(self._http)
        self._history_service = HistoryService(self._http)
        self._crawl_service = CrawlService(self._http)
        self._discovery_service = DiscoveryService(self._http)
        self._metadata_service = MetadataService(self._http)

    @property
    def history(self) -> HistoryService:
        """Access scan history operations."""
        return self._history_service

    @property
    def metadata(self) -> MetadataService:
        """Access API metadata such as finding type definitions."""
        return self._metadata_service

    def scan(self, url: str, scanners: list[str] | None = None) -> ScanResult:
        """Run a security scan against a single URL.

        Args:
            url: The target URL to scan.
            scanners: Optional list of scanner IDs to run. If omitted, all scanners run.

        Returns:
            A ScanResult containing findings, summary, and scan metadata.

        Raises:
            InvalidURLError: If the URL is malformed.
            AuthenticationError: If the API key is invalid.
            RateLimitError: If the rate limit is exceeded.
        """
        return self._scan_service.scan(url, scanners=scanners)

    def scan_crawl(self, url: str, urls: list[str] | None = None) -> CrawlResult:
        """Run a deep crawl scan across multiple pages of a target.

        Args:
            url: The root URL to crawl.
            urls: Optional additional URLs to include in the crawl.

        Returns:
            A CrawlResult with per-page findings and aggregate crawl info.
        """
        return self._crawl_service.scan_crawl(url, urls=urls)

    def discover_urls(self, url: str) -> DiscoveryResult:
        """Discover all crawlable URLs for a given target.

        Args:
            url: The root URL to discover pages from.

        Returns:
            A DiscoveryResult with a list of discovered URLs.
        """
        return self._discovery_service.discover_urls(url)

    def version(self) -> VersionInfo:
        """Retrieve the current API version and engine status.

        Returns:
            A VersionInfo object with version strings and status fields.
        """
        data: dict[str, Any] = self._http.get_unversioned("/api/version")
        return VersionInfo.from_dict(data)
