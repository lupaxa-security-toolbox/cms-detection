"""Public detect() API."""

from __future__ import annotations

from unittest.mock import patch
from urllib.parse import urlparse

import pytest

from lupaxa.cms_detection.api import candidate_urls, detect, detect_many
from lupaxa.cms_detection.exceptions import CmsDetectionError
from lupaxa.cms_detection.models import FetchResult


def test_empty_url_raises() -> None:
    with pytest.raises(CmsDetectionError, match="empty URL"):
        candidate_urls("   ")


def test_schemeless_prefers_https() -> None:
    assert candidate_urls("blog.example") == [
        "https://blog.example",
        "http://blog.example",
    ]


def _ok(url: str, html: str) -> FetchResult:
    return FetchResult(
        url=url if url.endswith("/") else url + "/",
        ok=True,
        error="",
        status=200,
        headers={},
        set_cookie="",
        html=html,
        body=html,
    )


def test_detect_returns_wordpress_from_generator() -> None:
    html = '<meta name="generator" content="WordPress 6.4.2">'
    with patch(
        "lupaxa.cms_detection.api.fetch_url",
        return_value=_ok("https://blog.example", html),
    ):
        result = detect("blog.example")
    assert result.cms == "WordPress"
    assert result.version == "6.4.2"
    assert result.error == ""
    assert result.url.startswith("https://")


def test_detect_fetch_failure_sets_error() -> None:
    failed = FetchResult(
        url="https://down.example",
        ok=False,
        error="Request failed: timeout",
        status=0,
        headers={},
        set_cookie="",
        html="",
        body="",
    )
    with patch("lupaxa.cms_detection.api.fetch_url", return_value=failed):
        result = detect("https://down.example")
    assert result.cms is None
    assert result.error.startswith("Request failed:")


def test_schemeless_falls_back_to_http() -> None:
    html = '<meta name="generator" content="WordPress 6.4.2">'
    failed = FetchResult(
        url="https://blog.example",
        ok=False,
        error="Request failed: TLS",
        status=0,
        headers={},
        set_cookie="",
        html="",
        body="",
    )

    def fake(url: str, **kwargs: object) -> FetchResult:
        if url.startswith("https://"):
            return failed
        return _ok(url, html)

    with patch("lupaxa.cms_detection.api.fetch_url", side_effect=fake):
        result = detect("blog.example")
    assert result.cms == "WordPress"
    assert result.url.startswith("http://")


def test_detect_many_preserves_order() -> None:
    html_wp = '<meta name="generator" content="WordPress 6.4">'
    html_unknown = "<html>nope</html>"

    def fake(url: str, **kwargs: object) -> FetchResult:
        host = urlparse(url).hostname or ""
        if host == "a.example":
            return _ok(url, html_wp)
        return _ok(url, html_unknown)

    with patch("lupaxa.cms_detection.api.fetch_url", side_effect=fake):
        results = detect_many(["https://b.example", "https://a.example"], workers=2)
    first_host = urlparse(results[0].url).hostname
    assert first_host == "b.example"
    assert results[1].cms == "WordPress"
    assert results[0].cms is None
