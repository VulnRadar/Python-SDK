from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


class VulnRadarError(Exception):
    """Base exception for all VulnRadar SDK errors."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class AuthenticationError(VulnRadarError):
    """Raised when the API key is invalid or missing."""

    def __init__(self, message: str = "Invalid or missing API key.") -> None:
        super().__init__(message, status_code=401)


class BadRequestError(VulnRadarError):
    """Raised when the API rejects the request due to invalid parameters."""

    def __init__(self, message: str = "Bad request. Check your parameters.") -> None:
        super().__init__(message, status_code=400)


class NotFoundError(VulnRadarError):
    """Raised when the requested resource does not exist."""

    def __init__(self, message: str = "Resource not found.") -> None:
        super().__init__(message, status_code=404)


class ForbiddenError(VulnRadarError):
    """Raised when access to a resource is forbidden."""

    def __init__(self, message: str = "You do not have permission to access this resource.") -> None:
        super().__init__(message, status_code=403)


class UnprocessableEntityError(VulnRadarError):
    """Raised when a target is unreachable or request cannot be processed."""

    def __init__(self, message: str = "The request could not be processed.") -> None:
        super().__init__(message, status_code=422)


class RateLimitError(VulnRadarError):
    """Raised when the API rate limit is exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded. Please wait before retrying.",
        rate_limit: "RateLimitInfo | None" = None,
    ) -> None:
        super().__init__(message, status_code=429)
        self.rate_limit = rate_limit

    @property
    def limit(self) -> int | None:
        return self.rate_limit.limit if self.rate_limit else None

    @property
    def used(self) -> int | None:
        return self.rate_limit.used if self.rate_limit else None

    @property
    def remaining(self) -> int | None:
        return self.rate_limit.remaining if self.rate_limit else None

    @property
    def resets_at(self) -> datetime | None:
        return self.rate_limit.resets_at if self.rate_limit else None


class ServerError(VulnRadarError):
    """Raised when the API returns a 5xx server error."""

    def __init__(self, message: str = "An internal server error occurred.", status_code: int = 500) -> None:
        super().__init__(message, status_code=status_code)


class InvalidURLError(VulnRadarError):
    """Raised when a provided URL fails validation."""

    def __init__(self, url: str) -> None:
        super().__init__(
            f"Invalid URL: '{url}'. Must be a valid URL using one of: "
            "http://, https://, ws://, wss://, ftp://, ftps://."
        )
        self.url = url


@dataclass(frozen=True)
class RateLimitInfo:
    """Rate limit metadata exposed through RateLimitError."""

    limit: int
    used: int
    remaining: int
    resets_at: datetime | None