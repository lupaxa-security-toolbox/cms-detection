"""Dataclass defaults for detection types."""

from __future__ import annotations

from lupaxa.cms_detection.exceptions import CmsDetectionError
from lupaxa.cms_detection.models import (
    CmsSignature,
    DetectResult,
    Evidence,
    FetchResult,
    PathProbe,
)


def test_cms_detection_error_is_exception() -> None:
    err = CmsDetectionError("empty URL")
    assert isinstance(err, Exception)
    assert str(err) == "empty URL"


def test_path_probe_defaults_to_http_200() -> None:
    probe = PathProbe(path="/readme.html", must_contain=("WordPress",))
    assert probe.allowed_status == (200,)


def test_detect_result_unknown_defaults() -> None:
    result = DetectResult(
        url="https://example.com",
        cms=None,
        version=None,
        confidence=None,
        evidence=(),
        candidates=(),
        error="",
    )
    assert result.cms is None
    assert result.error == ""


def test_fetch_result_failure() -> None:
    page = FetchResult(
        url="https://down.example",
        ok=False,
        error="Request failed: timeout",
        status=0,
        headers={},
        set_cookie="",
        html="",
        body="",
    )
    assert page.ok is False


def test_signature_name_round_trip() -> None:
    sig = CmsSignature(name="WordPress", meta_generator=("WordPress",))
    ev = Evidence(kind="meta_generator", value="WordPress 6.4", cms=sig.name)
    assert ev.cms == "WordPress"
