from __future__ import annotations

import os
from typing import Iterator

import pytest
from dotenv import load_dotenv

from vulnradar import VulnRadar


@pytest.fixture(scope="session", autouse=True)
def load_env() -> None:
    load_dotenv(override=False)


@pytest.fixture(scope="session")
def api_key(load_env: None) -> str:
    key = (
        os.getenv("VULNRADAR_API_KEY")
        or os.getenv("API_KEY")
        or os.getenv("VULNRADAR_KEY")
    )
    if not key:
        pytest.fail("VULNRADAR_API_KEY is missing. Set it in .env or environment variables.")
    return key


@pytest.fixture(scope="session")
def target_url() -> str:
    return os.getenv("VULNRADAR_TEST_URL", "https://example.com")


@pytest.fixture(scope="session")
def client(api_key: str) -> VulnRadar:
    return VulnRadar(api_key=api_key, timeout=90)


@pytest.fixture(scope="session")
def created_scan_ids() -> list[int]:
    return []


@pytest.fixture(scope="session", autouse=True)
def cleanup_created_scans(client: VulnRadar, created_scan_ids: list[int]) -> Iterator[None]:
    yield

    for scan_id in list(dict.fromkeys(created_scan_ids)):
        try:
            client.history.delete(scan_id)
        except Exception:
            pass
