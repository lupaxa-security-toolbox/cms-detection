"""fetch_url behaviour with a stubbed requests.get."""

from __future__ import annotations

from unittest.mock import Mock, patch

import requests

from lupaxa.cms_detection.fetch import USER_AGENT, fetch_url
from lupaxa.cms_detection.version import get_version


def test_user_agent_includes_version() -> None:
    assert f"lupaxa-cms-detection/{get_version()}" == USER_AGENT


def test_fetch_url_success_keeps_final_url() -> None:
    response = Mock()
    response.url = "https://www.example.com/"
    response.status_code = 200
    response.text = "<html>ok</html>"
    response.headers = {"Content-Type": "text/html", "Set-Cookie": "a=1"}
    with patch("lupaxa.cms_detection.fetch.requests.get", return_value=response) as get:
        page = fetch_url("https://example.com", delay=0, retries=1, timeout=2)
    get.assert_called_once()
    kwargs = get.call_args.kwargs
    assert kwargs["timeout"] == 2
    assert kwargs["headers"]["User-Agent"] == USER_AGENT
    assert page.ok is True
    assert page.url == "https://www.example.com/"
    assert page.html == "<html>ok</html>"
    assert page.headers["content-type"] == "text/html"
    assert page.set_cookie == "a=1"


def test_fetch_url_returns_error_after_retries() -> None:
    with patch(
        "lupaxa.cms_detection.fetch.requests.get",
        side_effect=requests.RequestException("timeout"),
    ):
        page = fetch_url("https://down.example", delay=0, retries=2, timeout=1)
    assert page.ok is False
    assert page.error.startswith("Request failed:")
    assert page.status == 0


def test_fetch_url_keeps_http_error_status() -> None:
    response = Mock()
    response.url = "https://example.com/wp-content/"
    response.status_code = 403
    response.text = "forbidden"
    response.headers = {}
    response.raise_for_status = Mock(side_effect=requests.HTTPError("403"))
    with patch("lupaxa.cms_detection.fetch.requests.get", return_value=response) as get:
        page = fetch_url("https://example.com/wp-content/", delay=0, retries=2, timeout=2)
    get.assert_called_once()
    assert page.ok is True
    assert page.status == 403
    assert page.body == "forbidden"
