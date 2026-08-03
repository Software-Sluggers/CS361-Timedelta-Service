import json
import os
from time import sleep

import pytest
import requests

PORT = os.environ.get("PORT", "5000")
BASE_URL = f"http://localhost:{PORT}"


def pytest_sessionstart(session: pytest.Session):
    """Fails suite if Docker is unhealthy."""

    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        response.raise_for_status()
        if response.json().get("status") != "ok":
            raise ValueError()
    except (requests.RequestException, ValueError):
        pytest.exit(
            "Container is not healthy. Remember to run the docker compose file!",
            returncode=1,
        )


@pytest.fixture
def base_url() -> str:
    return BASE_URL


@pytest.fixture
def get_timedelta(base_url: str):
    """GET from /timedelta with query params and return the status code and response body"""

    def _get(timestamp: str, operation: str, value: int, unit: str) -> tuple[int, dict]:
        params = {
            "timestamp": timestamp,
            "operation": operation,
            "value": value,
            "unit": unit,
        }
        print(f"{'=' * 60}")
        print(f"GET {base_url}/timedelta?{'&'.join(f'{k}={v}' for k, v in params.items())}")
        response = requests.get(f"{base_url}/timedelta", params=params, timeout=5)
        try:
            body = response.json()
            print(json.dumps(body, indent=2))
            print()
        except requests.exceptions.JSONDecodeError:
            body = {"error": "Response wasn't a valid JSON"}
        sleep(1)
        return response.status_code, body

    return _get
