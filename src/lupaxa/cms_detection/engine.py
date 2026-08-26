"""Score fetched pages against CMS signatures."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field

from bs4 import BeautifulSoup

from .models import CmsSignature, DetectResult, Evidence, FetchResult, PathProbe
from .signatures import SIGNATURES

FetchPath = Callable[..., FetchResult]

POINTS = {
    "meta_generator": 3,
    "header": 3,
    "path": 2,
    "cookie": 1,
    "script": 1,
}

_STRONG = frozenset({"meta_generator", "header"})
_WEAK = frozenset({"cookie", "script"})
_PASSIVE = frozenset({"meta_generator", "header", "cookie", "script"})


@dataclass
class ScoredCms:
    """Running score for one CMS."""

    name: str
    points: int = 0
    evidence: list[Evidence] = field(default_factory=list)
    version: str | None = None
    kinds: frozenset[str] = field(default_factory=frozenset)


def extract_version(text: str, patterns: tuple[str, ...]) -> str | None:
    """Return the first regex group match for ``patterns`` in ``text``."""
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(1)
    return None


def confidence_for(kinds: set[str]) -> str:
    """Map evidence kinds to high / medium / low."""
    strong = len(kinds & _STRONG)
    weak = len(kinds & _WEAK)
    passive = len(kinds & _PASSIVE)
    has_path = "path" in kinds
    if passive >= 2 or (strong >= 1 and has_path):
        return "high"
    if strong >= 1 or weak >= 2:
        return "medium"
    return "low"


def choose_winner(scores: list[ScoredCms]) -> ScoredCms | None:
    """Pick the best ``ScoredCms``, or ``None`` if ``scores`` is empty."""
    if not scores:
        return None
    return sorted(
        scores,
        key=lambda item: (-item.points, -len(item.kinds), item.version is None, item.name),
    )[0]


def _generator_contents(html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    values: list[str] = []
    for meta in soup.find_all("meta", attrs={"name": True}):
        if str(meta.get("name", "")).lower() == "generator":
            values.append(str(meta.get("content", "")))
    return values


def _script_sources(html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    return [str(tag["src"]) for tag in soup.find_all("script", src=True)]


def _cookie_names(set_cookie: str) -> list[str]:
    names: list[str] = []
    for part in set_cookie.split(","):
        first = part.split(";", 1)[0]
        if "=" not in first:
            continue
        names.append(first.split("=", 1)[0].strip().lower())
    return names


def score_passive(
    page: FetchResult,
    signatures: tuple[CmsSignature, ...] | None = None,
) -> list[ScoredCms]:
    """Score homepage signals only."""
    catalogue = signatures if signatures is not None else SIGNATURES
    generators = _generator_contents(page.html)
    scripts = _script_sources(page.html)
    header_names = {name.lower() for name in page.headers}
    cookie_names = _cookie_names(page.set_cookie)
    scored: list[ScoredCms] = []
    for sig in catalogue:
        evidence: list[Evidence] = []
        kinds: set[str] = set()
        points = 0
        version: str | None = None
        for needle in sig.meta_generator:
            for content in generators:
                if needle.lower() in content.lower():
                    evidence.append(Evidence("meta_generator", content, sig.name))
                    kinds.add("meta_generator")
                    points += POINTS["meta_generator"]
                    version = version or extract_version(content, sig.version_patterns)
                    break
        for header in sig.headers:
            if header.lower() in header_names:
                evidence.append(Evidence("header", header, sig.name))
                kinds.add("header")
                points += POINTS["header"]
        for cookie in sig.cookies:
            prefix = cookie.lower()
            if any(name.startswith(prefix) for name in cookie_names):
                evidence.append(Evidence("cookie", cookie, sig.name))
                kinds.add("cookie")
                points += POINTS["cookie"]
        for script_sig in sig.scripts:
            for src in scripts:
                if script_sig in src:
                    evidence.append(Evidence("script", src, sig.name))
                    kinds.add("script")
                    points += POINTS["script"]
                    break
        if points:
            scored.append(
                ScoredCms(
                    name=sig.name,
                    points=points,
                    evidence=evidence,
                    version=version,
                    kinds=frozenset(kinds),
                )
            )
    return scored


def probe_matches(page: FetchResult, probe: PathProbe) -> bool:
    """True when status is allowed and a snippet appears in body or headers."""
    if not page.ok or page.status not in probe.allowed_status:
        return False
    blob = page.body.lower() + "\n" + " ".join(page.headers.values()).lower()
    return any(snippet.lower() in blob for snippet in probe.must_contain)


def _apply_probes(
    scores: list[ScoredCms],
    sig: CmsSignature,
    probes: tuple[PathProbe, ...],
    base_url: str,
    fetch_path: FetchPath,
    delay: float,
    retries: int,
) -> None:
    current = next((item for item in scores if item.name == sig.name), None)
    for probe in probes:
        page = fetch_path(
            base_url.rstrip("/") + probe.path,
            delay=delay,
            retries=retries,
            timeout=5,
        )
        if not probe_matches(page, probe):
            continue
        if current is None:
            current = ScoredCms(name=sig.name)
            scores.append(current)
        current.points += POINTS["path"]
        current.evidence.append(Evidence("path", probe.path, sig.name))
        current.kinds = frozenset(set(current.kinds) | {"path"})
        if current.version is None:
            current.version = extract_version(page.body, sig.version_patterns)


def run_detection(
    homepage: FetchResult,
    *,
    active: bool,
    fetch_path: FetchPath,
    delay: float = 0,
    retries: int = 2,
) -> DetectResult:
    """Score homepage, optionally probe, and build a ``DetectResult``."""
    scores = score_passive(homepage)
    winner = choose_winner(scores)
    winner_kinds = set(winner.kinds) if winner else set()
    have_version = bool(winner and winner.version)
    confident = bool(winner and confidence_for(winner_kinds) in {"medium", "high"})
    by_name = {sig.name: sig for sig in SIGNATURES}
    top = sorted(scores, key=lambda item: (-item.points, item.name))[:2]
    if not (confident and have_version) and top:
        for item in top:
            sig = by_name[item.name]
            _apply_probes(scores, sig, sig.confirm_paths, homepage.url, fetch_path, delay, retries)
        if active:
            for item in top:
                sig = by_name[item.name]
                _apply_probes(
                    scores, sig, sig.active_paths, homepage.url, fetch_path, delay, retries
                )
    elif not (confident and have_version) and active:
        for sig in SIGNATURES:
            _apply_probes(scores, sig, sig.confirm_paths, homepage.url, fetch_path, delay, retries)
        for item in list(scores):
            sig = by_name[item.name]
            _apply_probes(scores, sig, sig.active_paths, homepage.url, fetch_path, delay, retries)
    winner = choose_winner(scores)
    all_evidence: list[Evidence] = []
    for item in scores:
        all_evidence.extend(item.evidence)
    if winner is None:
        return DetectResult(
            url=homepage.url,
            cms=None,
            version=None,
            confidence=None,
            evidence=tuple(all_evidence),
            candidates=(),
            error="",
        )
    others = tuple(sorted(item.name for item in scores if item.name != winner.name))
    return DetectResult(
        url=homepage.url,
        cms=winner.name,
        version=winner.version,
        confidence=confidence_for(set(winner.kinds)),
        evidence=tuple(all_evidence),
        candidates=others,
        error="",
    )
