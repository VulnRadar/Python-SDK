from __future__ import annotations

import time
from typing import Any
from urllib.parse import urlsplit

import requests
from requests import Response, Session

from .config import VulnRadarConfig
from .exceptions import (
    AuthenticationError,
    BadRequestError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    ServerError,
    UnprocessableEntityError,
    VulnRadarError,
)
from .utils.rate_limit import RateLimitInfo, parse_rate_limit_headers


class HTTPClient:
    """Low-level HTTP client that wraps requests with auth, retries, and error handling."""

    def __init__(self, config: VulnRadarConfig) -> None:
        self._config = config
        self._session = Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json",
            }
        )

    def get(self, path: str, *, versioned: bool = True) -> dict[str, Any]:
        """Perform an authenticated GET request.

        Args:
            path: The API path (e.g. '/history').
            versioned: If False, uses the unversioned base URL for paths like /api/version.

        Returns:
            Parsed JSON response as a dict.
        """
        url = (self._config.base_url if versioned else self._base_origin()) + path
        return self._request("GET", url)

    def get_unversioned(self, path: str) -> dict[str, Any]:
        """Perform a GET request against an unversioned endpoint.

        The path is appended directly to the domain root (no /api/v2 prefix).

        Args:
            path: Full path from domain root (e.g. '/api/version').

        Returns:
            Parsed JSON response as a dict.
        """
        return self._request("GET", self._base_origin() + path)

    def post(self, path: str, json: dict[str, Any]) -> dict[str, Any]:
        """Perform an authenticated POST request.

        Args:
            path: The API path (e.g. '/scan').
            json: Request body as a dict.

        Returns:
            Parsed JSON response as a dict.
        """
        url = self._config.base_url + path
        return self._request("POST", url, json=json)

    def delete(self, path: str) -> dict[str, Any]:
        """Perform an authenticated DELETE request.

        Args:
            path: The API path (e.g. '/history/123').

        Returns:
            Parsed JSON response as a dict.
        """
        url = self._config.base_url + path
        return self._request("DELETE", url)

    def _base_origin(self) -> str:
        parsed = urlsplit(self._config.base_url)
        return f"{parsed.scheme}://{parsed.netloc}"

    def _request(
        self,
        method: str,
        url: str,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        last_exc: Exception | None = None

        for attempt in range(max(1, self._config.retries)):
            try:
                response = self._session.request(
                    method,
                    url,
                    json=json,
                    timeout=self._config.timeout,
                )
                self._raise_for_status(response)
                return response.json()  # may raise if response is not JSON
            except RateLimitError:
                raise
            except (AuthenticationError, BadRequestError, NotFoundError):
                raise
            except ServerError as exc:
                last_exc = exc
                if attempt < self._config.retries - 1:
                    time.sleep(self._config.retry_backoff * (2**attempt))
            except requests.exceptions.Timeout as exc:
                last_exc = VulnRadarError(f"Request timed out after {self._config.timeout}s.")
                if attempt < self._config.retries - 1:
                    time.sleep(self._config.retry_backoff * (2**attempt))
            except requests.exceptions.ConnectionError as exc:
                last_exc = VulnRadarError(f"Connection error: {exc}")
                if attempt < self._config.retries - 1:
                    time.sleep(self._config.retry_backoff * (2**attempt))

        raise last_exc or VulnRadarError("Request failed after retries.")

    def _raise_for_status(self, response: Response) -> None:
        status = response.status_code
        if status < 400:
            # Detect redirect-to-login: response is 2xx but content is HTML (not JSON)
            content_type = response.headers.get("Content-Type", "")
            if "text/html" in content_type:
                raise AuthenticationError(
                    "API returned an HTML login page instead of JSON. "
                    "The Authorization header may not be accepted for this endpoint."
                )
            return

        try:
            body = response.json()
            message = body.get("message") or body.get("error") or response.text
        except Exception:
            message = response.text

        if status == 400:
            raise BadRequestError(message)
        elif status == 401:
            raise AuthenticationError(message)
        elif status == 404:
            raise NotFoundError(message)
        elif status == 403:
            raise ForbiddenError(message)
        elif status == 422:
            raise UnprocessableEntityError(message)
        elif status == 429:
            rate_limit = parse_rate_limit_headers(response.headers)
            rl_info = (
                RateLimitInfo(
                    limit=rate_limit.limit,
                    used=rate_limit.used,
                    remaining=rate_limit.remaining,
                    resets_at=rate_limit.resets_at,
                )
                if rate_limit
                else None
            )
            raise RateLimitError(message, rate_limit=rl_info)
        elif status >= 500:
            raise ServerError(message, status_code=status)
        else:
            raise VulnRadarError(message, status_code=status)
