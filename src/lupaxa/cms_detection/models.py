"""Value types for CMS detection."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Evidence:
    """One matching signal."""

    kind: str
    value: str
    cms: str


@dataclass(frozen=True)
class DetectResult:
    """Outcome of detecting one URL."""

    url: str
    cms: str | None
    version: str | None
    confidence: str | None
    evidence: tuple[Evidence, ...]
    candidates: tuple[str, ...]
    error: str


@dataclass(frozen=True)
class FetchResult:
    """One HTTP GET outcome. Failures set ``ok=False`` and ``error``."""

    url: str
    ok: bool
    error: str
    status: int
    headers: dict[str, str]
    set_cookie: str
    html: str
    body: str


@dataclass(frozen=True)
class PathProbe:
    """An extra path request that needs a content match."""

    path: str
    must_contain: tuple[str, ...]
    allowed_status: tuple[int, ...] = (200,)


@dataclass(frozen=True)
class CmsSignature:
    """Passive and active signals for one CMS."""

    name: str
    meta_generator: tuple[str, ...] = ()
    headers: tuple[str, ...] = ()
    cookies: tuple[str, ...] = ()
    scripts: tuple[str, ...] = ()
    confirm_paths: tuple[PathProbe, ...] = ()
    active_paths: tuple[PathProbe, ...] = ()
    version_patterns: tuple[str, ...] = ()
