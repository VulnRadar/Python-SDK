from __future__ import annotations

from ..http import HTTPClient
from ..models.history import HistoryList
from ..models.scan_result import ScanResult


class HistoryService:
    """Access and retrieve past scan history."""

    def __init__(self, http: HTTPClient) -> None:
        self._http = http

    def list(self) -> HistoryList:
        """Retrieve the last 100 scans.

        Returns:
            A HistoryList containing scan summaries.
        """
        data = self._http.get("/history")
        return HistoryList.from_dict(data)

    def get(self, scan_id: str) -> ScanResult:
        """Retrieve the full details of a specific scan.

        Args:
            scan_id: The unique identifier of the scan in history.

        Returns:
            A ScanResult with complete findings and metadata.

        Raises:
            NotFoundError: If no scan with the given ID exists.
        """
        data = self._http.get(f"/history/{scan_id}")
        return ScanResult.from_dict(data)
