BASE_URL: str = "https://vulnradar.dev/api/v2"
VERSION_URL: str = "https://vulnradar.dev/api/version"

DEFAULT_TIMEOUT: int = 30
DEFAULT_RETRIES: int = 3
DEFAULT_RETRY_BACKOFF: float = 0.5

RATE_LIMIT_HEADER: str = "X-RateLimit-Limit"
RATE_LIMIT_REMAINING_HEADER: str = "X-RateLimit-Remaining"
RATE_LIMIT_RESET_HEADER: str = "X-RateLimit-Reset"
RETRY_AFTER_HEADER: str = "Retry-After"
