from __future__ import annotations

from dataclasses import dataclass, field

from ..enums import Severity


@dataclass
class FindingType:
    """A classification type for security findings."""

    id: str
    type: str
    title: str
    category: str
    severity: Severity

    @classmethod
    def from_dict(cls, data: dict) -> "FindingType":
        return cls(
            id=data.get("id", ""),
            type=data.get("type", ""),
            title=data.get("title", ""),
            category=data.get("category", ""),
            severity=Severity(data.get("severity", "info")),
        )
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FindingType):
            return NotImplemented
        return self.id == other.id or self.type == other.type or self.title == other.title


@dataclass
class FindingTypesResult:
    """The full catalog of supported finding types."""

    version: str
    count: int
    types: list[FindingType] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "FindingTypesResult":
        types = [FindingType.from_dict(t) for t in data.get("types", [])]
        return cls(
            version=data.get("version", ""),
            count=data.get("count", len(types)),
            types=types,
        )
