from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Summary:
    """Aggregated vulnerability counts from a scan."""

    total: int
    critical: int
    high: int
    medium: int
    low: int
    info: int

    @classmethod
    def from_dict(cls, data: dict) -> "Summary":
        return cls(
            total=data.get("total", 0),
            critical=data.get("critical", 0),
            high=data.get("high", 0),
            medium=data.get("medium", 0),
            low=data.get("low", 0),
            info=data.get("info", 0),
        )
