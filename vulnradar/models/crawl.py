from __future__ import annotations

from dataclasses import dataclass, field

from .findings import Finding
from .summary import Summary


@dataclass
class CrawlPage:
    """Result of scanning a single page during a crawl."""

    url: str
    findings: list[Finding]
    summary: Summary
    duration: float
    response_headers: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "CrawlPage":
        return cls(
            url=data.get("url", ""),
            findings=[Finding.from_dict(f) for f in data.get("findings", [])],
            summary=Summary.from_dict(data.get("summary", {})),
            duration=float(data.get("duration", 0.0)),
            response_headers=data.get("responseHeaders", {}),
        )


@dataclass
class CrawlInfo:
    """Metadata about a crawl operation."""

    total_pages: int
    total_findings: int
    duration: float


@dataclass
class CrawlResult:
    """Full result of a deep crawl scan."""

    crawl: CrawlInfo
    pages: list[CrawlPage] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "CrawlResult":
        crawl_data = data.get("crawl", {})
        pages = [CrawlPage.from_dict(p) for p in crawl_data.get("pages", [])]
        crawl = CrawlInfo(
            total_pages=int(crawl_data.get("totalPages", len(pages))),
            total_findings=sum(p.summary.total for p in pages),
            duration=float(data.get("duration", 0.0)),
        )
        return cls(crawl=crawl, pages=pages)


@dataclass
class DiscoveryResult:
    """Result of URL discovery for a target domain."""

    urls: list[str]
    total: int

    @classmethod
    def from_dict(cls, data: dict) -> "DiscoveryResult":
        urls = data.get("urls", [])
        return cls(
            urls=urls,
            total=data.get("total", len(urls)),
        )
