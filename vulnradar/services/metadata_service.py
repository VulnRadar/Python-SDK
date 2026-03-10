from __future__ import annotations

from ..http import HTTPClient
from ..models.finding_types import FindingTypesResult


class MetadataService:
    """Provides access to static API metadata such as finding type definitions."""

    def __init__(self, http: HTTPClient) -> None:
        self._http = http

    def finding_types(self) -> FindingTypesResult:
        """Retrieve the full catalog of supported finding types.

        This is a public endpoint and does not require authentication,
        but the SDK sends the auth header regardless for consistency.

        Returns:
            A FindingTypesResult containing all finding type definitions.
        """
        data = self._http.get("/finding-types")
        return FindingTypesResult.from_dict(data)
