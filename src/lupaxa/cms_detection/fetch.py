"""HTTP GET helper for CMS detection."""

from __future__ import annotations

import time

import requests

from .models import FetchResult
from .version import get_version

USER_AGENT = f"lupaxa-cms-detection/{get_version()}"


def fetch_url(
    url: str,
    *,
    delay: float = 0,
    retries: int = 2,
    timeout: float = 10,
) -> FetchResult:
    """GET ``url`` and return a ``FetchResult``. Network errors are not raised."""
    last_error = "Unknown error"
    attempts = max(1, retries)
    for attempt in range(attempts):
        if delay:
            time.sleep(delay)
        try:
            response = requests.get(
                url,
                timeout=timeout,
                headers={"User-Agent": USER_AGENT},
            )
            headers = {key.lower(): value for key, value in response.headers.items()}
            return FetchResult(
                url=str(response.url),
                ok=True,
                error="",
                status=int(response.status_code),
                headers=headers,
                set_cookie=headers.get("set-cookie", ""),
                html=response.text,
                body=response.text,
            )
        except requests.RequestException as exc:
            last_error = f"Request failed: {exc}"
            if attempt == attempts - 1:
                break
    return FetchResult(
        url=url,
        ok=False,
        error=last_error,
        status=0,
        headers={},
        set_cookie="",
        html="",
        body="",
    )
