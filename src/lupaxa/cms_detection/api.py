"""Public CMS detection API."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed

from .engine import run_detection
from .exceptions import CmsDetectionError
from .fetch import fetch_url
from .models import DetectResult, FetchResult


def candidate_urls(raw: str) -> list[str]:
    """Expand a user-supplied host or URL into fetch candidates."""
    value = raw.strip()
    if not value:
        raise CmsDetectionError("empty URL")
    if value.startswith(("http://", "https://")):
        return [value]
    return [f"https://{value}", f"http://{value}"]


def _homepage(url: str, *, delay: float, retries: int, timeout: float) -> FetchResult:
    last: FetchResult | None = None
    for candidate in candidate_urls(url):
        last = fetch_url(candidate, delay=delay, retries=retries, timeout=timeout)
        if last.ok:
            return last
    assert last is not None
    return last


def detect(
    url: str,
    *,
    active: bool = False,
    delay: float = 0,
    retries: int = 2,
    timeout: float = 10,
) -> DetectResult:
    """Detect the CMS used by ``url``."""
    homepage = _homepage(url, delay=delay, retries=retries, timeout=timeout)
    if not homepage.ok:
        return DetectResult(
            url=homepage.url,
            cms=None,
            version=None,
            confidence=None,
            evidence=(),
            candidates=(),
            error=homepage.error,
        )
    return run_detection(
        homepage,
        active=active,
        fetch_path=fetch_url,
        delay=delay,
        retries=retries,
    )


def detect_many(
    urls: list[str],
    *,
    workers: int = 10,
    active: bool = False,
    delay: float = 0,
    retries: int = 2,
    timeout: float = 10,
) -> list[DetectResult]:
    """Detect many URLs; returned list matches input order."""
    if not urls:
        return []
    results: list[DetectResult | None] = [None] * len(urls)
    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        futures = {
            pool.submit(
                detect,
                item,
                active=active,
                delay=delay,
                retries=retries,
                timeout=timeout,
            ): index
            for index, item in enumerate(urls)
        }
        for future in as_completed(futures):
            results[futures[future]] = future.result()
    return [item for item in results if item is not None]
