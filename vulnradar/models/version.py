from __future__ import annotations

from dataclasses import dataclass


@dataclass
class VersionInfo:
    """API version and engine metadata."""

    current: str
    latest: str
    engine: str
    status: str
    message: str | None

    @classmethod
    def from_dict(cls, data: dict) -> "VersionInfo":
        return cls(
            current=data.get("current", ""),
            latest=data.get("latest", ""),
            engine=data.get("engine", ""),
            status=data.get("status", ""),
            message=data.get("message"),
        )
