from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .findings import Finding
from .summary import Summary


@dataclass
class ScanResult:
    """Full result of a single URL scan."""

    url: str
    scanned_at: datetime
    duration: float
    findings: list[Finding]
    summary: Summary
    response_headers: dict[str, str]
    scan_history_id: int | None
    notes: str | None

    @classmethod
    def from_dict(cls, data: dict) -> "ScanResult":
        raw_ts = data.get("scannedAt", "")
        scanned_at = datetime.fromisoformat(raw_ts.replace("Z", "+00:00")) if raw_ts else datetime.utcnow()

        return cls(
            url=data.get("url", ""),
            scanned_at=scanned_at,
            duration=float(data.get("duration", 0.0)),
            findings=[Finding.from_dict(f) for f in data.get("findings", [])],
            summary=Summary.from_dict(data.get("summary", {})),
            response_headers=data.get("responseHeaders", {}),
            scan_history_id=(int(data["scanHistoryId"]) if data.get("scanHistoryId") is not None else None),
            notes=data.get("notes"),
        )
