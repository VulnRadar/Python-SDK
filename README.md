# VulnRadar Python SDK

A production-ready Python SDK for the [VulnRadar](https://vulnradar.dev) security scanning API. Clean, fully typed, and designed for developer-friendly integration.

---

## Overview

VulnRadar scans web targets for security vulnerabilities, exposing findings categorized by severity (critical, high, medium, low, info). This SDK wraps the REST API with:

- Full type hints and dataclass-based response models
- Automatic authentication header injection
- Structured error handling with custom exceptions
- Rate limit awareness via response header parsing
- Configurable timeout and retry logic
- Support for single scans, deep crawl scans, URL discovery, and history retrieval

---

## Installation

```bash
pip install vulnradar
```

Requires Python 3.10+.

---

## Quickstart

```python
from vulnradar import VulnRadar

client = VulnRadar(api_key="your-api-key")

result = client.scan("https://example.com")

print(f"Total findings: {result.summary.total}")
print(f"Critical: {result.summary.critical}")

for finding in result.findings:
    print(f"[{finding.severity.value.upper()}] {finding.title}")
```

---

## Authentication

All requests are authenticated using a Bearer token in the `Authorization` header. Pass your API key when constructing the client:

```python
client = VulnRadar(api_key="your-api-key")
```

---

## Configuration

```python
client = VulnRadar(
    api_key="your-api-key",
    timeout=60,          # HTTP timeout in seconds (default: 30)
    retries=5,           # Retry attempts on server errors (default: 3)
    base_url="https://vulnradar.dev/api/v2",  # Custom base URL (optional)
)
```

---

## Running Scans

### Single URL Scan

```python
result = client.scan("https://example.com")

# Optional: run only selected scanners.
result = client.scan("https://example.com", scanners=["headers", "ssl"])

print(result.url)
print(result.scanned_at)
print(result.duration)
print(result.scan_history_id)

for finding in result.findings:
    print(finding.type, finding.severity, finding.title)
    print(finding.description)
    print(finding.remediation)
```

Supported target protocols: `http://`, `https://`, `ws://`, `wss://`, `ftp://`, `ftps://`.

**ScanResult fields:**

| Field              | Type                  | Description                        |
|--------------------|-----------------------|------------------------------------|
| `url`              | `str`                 | Scanned URL                        |
| `scanned_at`       | `datetime`            | Timestamp of the scan              |
| `duration`         | `float`               | Scan duration in seconds           |
| `findings`         | `list[Finding]`       | List of security findings          |
| `summary`          | `Summary`             | Aggregated finding counts          |
| `response_headers` | `dict[str, str]`      | HTTP headers from the target       |
| `scan_history_id`  | `int \| None`         | ID in scan history                 |
| `notes`            | `str \| None`         | Optional scan notes                |

---

## Crawl Scans

Perform a deep crawl across multiple pages of a target:

```python
result = client.scan_crawl("https://example.com")

print(f"Pages scanned: {result.crawl.total_pages}")
print(f"Total findings: {result.crawl.total_findings}")

for page in result.pages:
    print(f"{page.url} — {page.summary.total} findings")
```

You can also provide a list of specific URLs to include:

```python
result = client.scan_crawl(
    "https://example.com",
    urls=["https://example.com/login", "https://example.com/admin"],
)
```

---

## Discover URLs

Discover all crawlable URLs for a target before running a crawl scan:

```python
discovery = client.discover_urls("https://example.com")

print(f"Found {discovery.total} URLs")
for url in discovery.urls:
    print(url)
```

---

## Scan History

### List Recent Scans

```python
history = client.history.list()

for scan in history.scans:
    print(scan.id, scan.url, scan.scanned_at)
    print(f"  Findings: {scan.findings_count}")
```

### Get a Specific Scan

```python
result = client.history.get(123)

print(result.url)
for finding in result.findings:
    print(finding.title, finding.severity)
```

### Delete a Scan

```python
deleted = client.history.delete(123)
print(deleted.success)
print(deleted.message)
```

---

## Finding Types

Retrieve the full catalog of supported finding types:

```python
catalog = client.metadata.finding_types()

print(f"Version: {catalog.version}")
print(f"Total types: {catalog.count}")

for ft in catalog.types:
    print(f"[{ft.severity.value}] {ft.title} ({ft.category})")
```

---

## Version Check

```python
info = client.version()

print(info.current)
print(info.latest)
print(info.engine)
print(info.status)
```

---

## Error Handling

All exceptions inherit from `VulnRadarError`:

```python
from vulnradar import (
    VulnRadar,
    VulnRadarError,
    AuthenticationError,
    BadRequestError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    ServerError,
    InvalidURLError,
    UnprocessableEntityError,
)

client = VulnRadar(api_key="your-api-key")

try:
    result = client.scan("https://example.com")
except InvalidURLError as e:
    print(f"Bad URL: {e.url}")
except AuthenticationError:
    print("Invalid or expired API key.")
except RateLimitError as e:
    print(f"Rate limited. Resets at: {e.resets_at}")
    print(f"Limit: {e.limit}, Remaining: {e.remaining}")
except NotFoundError:
    print("Resource not found.")
except ServerError as e:
    print(f"Server error {e.status_code}: {e.message}")
except VulnRadarError as e:
    print(f"SDK error: {e.message}")
```

### Exception Reference

| Exception           | HTTP Status | Description                          |
|---------------------|-------------|--------------------------------------|
| `AuthenticationError` | 401       | Invalid or missing API key           |
| `BadRequestError`   | 400         | Malformed request or invalid params  |
| `ForbiddenError`    | 403         | Authenticated but not permitted      |
| `NotFoundError`     | 404         | Requested resource does not exist    |
| `UnprocessableEntityError` | 422  | Target is unreachable/not processable |
| `RateLimitError`    | 429         | Rate limit exceeded                  |
| `ServerError`       | 5xx         | API-side internal error              |
| `InvalidURLError`   | —           | URL failed client-side validation    |

---

## Rate Limits

The SDK automatically parses rate limit headers from every response. When you hit a rate limit, the `RateLimitError` exception exposes:

```python
except RateLimitError as e:
    print(e.limit)       # Total allowed requests
    print(e.used)        # Requests used
    print(e.remaining)   # Requests remaining
    print(e.resets_at)   # datetime when limit resets
```

Headers parsed:
- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`
- `X-RateLimit-Reset`
- `Retry-After`

Default API key quota: `50 requests per 24 hours`.

---

## Severity Enum

```python
from vulnradar import Severity

Severity.CRITICAL  # "critical"
Severity.HIGH      # "high"
Severity.MEDIUM    # "medium"
Severity.LOW       # "low"
Severity.INFO      # "info"
```

Filter findings by severity:

```python
critical = [f for f in result.findings if f.severity == Severity.CRITICAL]
```

---

## Best Practices

**Handle rate limits gracefully:**

```python
import time
from vulnradar import VulnRadar, RateLimitError

client = VulnRadar(api_key="your-api-key")

def safe_scan(url: str):
    try:
        return client.scan(url)
    except RateLimitError as e:
        if e.resets_at:
            wait = (e.resets_at - datetime.now(timezone.utc)).total_seconds()
            time.sleep(max(wait, 1))
        return client.scan(url)
```

**Use history to avoid redundant scans:**

```python
history = client.history.list()
already_scanned = {s.url for s in history.scans}

if target_url not in already_scanned:
    result = client.scan(target_url)
```

**Pre-discover URLs before crawling:**

```python
discovery = client.discover_urls("https://example.com")
if discovery.total > 0:
    result = client.scan_crawl("https://example.com", urls=discovery.urls)
```

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes with full type hints
4. Run tests: `pytest`
5. Submit a pull request

All contributions must pass lint and type checking.

---

## License

MIT — see [LICENSE](LICENSE) for details.
