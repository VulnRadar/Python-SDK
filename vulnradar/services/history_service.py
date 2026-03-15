from __future__ import annotations

from ..http import HTTPClient
from ..models.history import DeleteScanResult, HistoryList
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

    def get(self, scan_id: int | str) -> ScanResult:
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

    def delete(self, scan_id: int | str) -> DeleteScanResult:
        """Delete a scan from history.

        Args:
            scan_id: The identifier of the scan to delete.

        Returns:
            A DeleteScanResult confirming deletion.

        Raises:
            AuthenticationError: If the API key is invalid.
            NotFoundError: If no scan with the given ID exists.
            VulnRadarError: If permission is denied or request fails.
        """
        data = self._http.delete(f"/history/{scan_id}")
        return DeleteScanResult.from_dict(data)
