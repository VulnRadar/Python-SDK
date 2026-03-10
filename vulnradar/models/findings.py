from __future__ import annotations

from dataclasses import dataclass

from ..enums import Severity


@dataclass
class Finding:
    """A single security finding from a scan."""

    type: str
    title: str
    severity: Severity
    description: str
    remediation: str

    @classmethod
    def from_dict(cls, data: dict) -> "Finding":
        return cls(
            type=data.get("type", ""),
            title=data.get("title", ""),
            severity=Severity(data.get("severity", "info")),
            description=data.get("description", ""),
            remediation=data.get("remediation", ""),
        )
