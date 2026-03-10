from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from .summary import Summary


@dataclass
class HistoryScan:
    """A scan entry from the scan history list."""

    id: str
    url: str
    summary: Summary
    findings_count: int
    duration: float
    scanned_at: datetime
    source: str
    notes: str | None
    tags: list[str]

    @classmethod
    def from_dict(cls, data: dict) -> "HistoryScan":
        raw_ts = data.get("scanned_at", "")
        scanned_at = datetime.fromisoformat(raw_ts.replace("Z", "+00:00")) if raw_ts else datetime.utcnow()

        return cls(
            id=data.get("id", ""),
            url=data.get("url", ""),
            summary=Summary.from_dict(data.get("summary", {})),
            findings_count=int(data.get("findings_count", 0)),
            duration=float(data.get("duration", 0.0)),
            scanned_at=scanned_at,
            source=data.get("source", ""),
            notes=data.get("notes"),
            tags=data.get("tags", []),
        )


@dataclass
class HistoryList:
    """Paginated list of scan history entries."""

    scans: list[HistoryScan] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "HistoryList":
        return cls(
            scans=[HistoryScan.from_dict(s) for s in data.get("scans", [])],
        )
