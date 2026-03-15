from __future__ import annotations

from datetime import datetime
from typing import Any

import pytest

from vulnradar import (
    CrawlResult,
    DiscoveryResult,
    FindingTypesResult,
    NotFoundError,
    ScanResult,
    Severity,
    VersionInfo,
    VulnRadar,
)


def _assert_summary(summary: Any) -> None:
    assert hasattr(summary, "critical")
    assert hasattr(summary, "high")
    assert hasattr(summary, "medium")
    assert hasattr(summary, "low")
    assert hasattr(summary, "info")
    assert hasattr(summary, "total")
    assert summary.total >= 0


@pytest.fixture(scope="module")
def scan_for_history(client: VulnRadar, target_url: str, created_scan_ids: list[int]) -> ScanResult:
    result = client.scan(target_url, scanners=["headers", "ssl"])
    assert result.scan_history_id is not None
    created_scan_ids.append(result.scan_history_id)
    return result


@pytest.fixture(scope="module")
def discovered_urls(client: VulnRadar, target_url: str) -> DiscoveryResult:
    result = client.discover_urls(target_url)
    assert isinstance(result, DiscoveryResult)
    assert result.total >= 0
    assert isinstance(result.urls, list)
    return result


def test_endpoint_version_public(client: VulnRadar) -> None:
    result = client.version()

    assert isinstance(result, VersionInfo)
    assert result.current
    assert result.latest
    assert result.engine
    assert result.status in {"up-to-date", "behind", "ahead"}


def test_endpoint_finding_types_public(client: VulnRadar) -> None:
    result = client.metadata.finding_types()

    assert isinstance(result, FindingTypesResult)
    assert result.count >= 1
    assert len(result.types) >= 1
    assert result.version

    sample = result.types[0]
    assert sample.id
    assert sample.title
    assert sample.category
    assert isinstance(sample.severity, Severity)


def test_endpoint_scan_create_default_scanners(
    client: VulnRadar,
    target_url: str,
    created_scan_ids: list[int],
) -> None:
    result = client.scan(target_url)

    assert isinstance(result, ScanResult)
    assert result.url
    assert isinstance(result.scanned_at, datetime)
    assert result.duration >= 0
    _assert_summary(result.summary)

    assert isinstance(result.findings, list)
    for finding in result.findings:
        assert finding.type
        assert finding.title
        assert isinstance(finding.severity, Severity)
        assert isinstance(finding.description, str)
        assert isinstance(finding.remediation, str)

    assert result.scan_history_id is not None
    created_scan_ids.append(result.scan_history_id)


def test_endpoint_scan_create_with_explicit_scanners(scan_for_history: ScanResult) -> None:
    assert isinstance(scan_for_history, ScanResult)
    assert scan_for_history.url
    assert isinstance(scan_for_history.scanned_at, datetime)
    _assert_summary(scan_for_history.summary)
    assert scan_for_history.scan_history_id is not None


def test_endpoint_history_list_contains_recent_scan(
    client: VulnRadar,
    scan_for_history: ScanResult,
) -> None:
    history = client.history.list()

    assert len(history.scans) >= 1

    ids = {entry.id for entry in history.scans}
    assert scan_for_history.scan_history_id in ids

    for entry in history.scans:
        assert entry.id > 0
        assert entry.url
        assert isinstance(entry.scanned_at, datetime)
        assert entry.findings_count >= 0
        assert entry.duration >= 0
        _assert_summary(entry.summary)


def test_endpoint_history_get_by_id(client: VulnRadar, scan_for_history: ScanResult) -> None:
    assert scan_for_history.scan_history_id is not None

    detail = client.history.get(scan_for_history.scan_history_id)

    assert isinstance(detail, ScanResult)
    assert detail.url
    assert isinstance(detail.scanned_at, datetime)
    assert detail.duration >= 0
    _assert_summary(detail.summary)
    assert isinstance(detail.findings, list)


def test_endpoint_scan_crawl_discover(discovered_urls: DiscoveryResult, target_url: str) -> None:
    assert discovered_urls.total == len(discovered_urls.urls)

    if discovered_urls.urls:
        assert any(url.startswith("http") for url in discovered_urls.urls)
        assert any(target_url.split("//", 1)[1].split("/", 1)[0] in url for url in discovered_urls.urls)


def test_endpoint_scan_crawl(client: VulnRadar, target_url: str, discovered_urls: DiscoveryResult) -> None:
    selected = discovered_urls.urls[:3] if discovered_urls.urls else None
    result = client.scan_crawl(target_url, urls=selected)

    assert isinstance(result, CrawlResult)
    assert result.crawl.total_pages >= 0
    assert result.crawl.total_findings >= 0
    assert result.crawl.duration >= 0
    assert isinstance(result.pages, list)

    for page in result.pages:
        assert page.url
        assert page.duration >= 0
        _assert_summary(page.summary)
        assert isinstance(page.findings, list)


def test_endpoint_history_delete(client: VulnRadar, target_url: str) -> None:
    created = client.scan(target_url, scanners=["headers"])
    assert created.scan_history_id is not None

    deleted = client.history.delete(created.scan_history_id)
    assert deleted.success is True
    assert deleted.message

    with pytest.raises(NotFoundError):
        client.history.get(created.scan_history_id)
