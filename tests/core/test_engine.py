"""Passive scoring and winner selection."""

from __future__ import annotations

from lupaxa.cms_detection.engine import (
    ScoredCms,
    choose_winner,
    confidence_for,
    probe_matches,
    run_detection,
    score_passive,
)
from lupaxa.cms_detection.models import FetchResult, PathProbe


def _page(
    *,
    html: str = "<html></html>",
    headers: dict[str, str] | None = None,
    set_cookie: str = "",
) -> FetchResult:
    return FetchResult(
        url="https://target.example/",
        ok=True,
        error="",
        status=200,
        headers=headers or {},
        set_cookie=set_cookie,
        html=html,
        body=html,
    )


def test_wordpress_generator_is_medium_and_extracts_version() -> None:
    html = '<meta name="generator" content="WordPress 6.4.2">'
    scores = score_passive(_page(html=html))
    wp = next(item for item in scores if item.name == "WordPress")
    assert wp.points == 3
    assert wp.version == "6.4.2"
    assert confidence_for(set(wp.kinds)) == "medium"


def test_shopify_header_and_script_is_high() -> None:
    html = '<script src="https://cdn.shopify.com/s/files/x.js"></script>'
    scores = score_passive(_page(html=html, headers={"x-shopid": "1"}))
    shop = next(item for item in scores if item.name == "Shopify")
    assert shop.points == 4
    assert confidence_for(set(shop.kinds)) == "high"


def test_wix_script_only_is_low() -> None:
    html = '<script src="https://static.parastorage.com/x.js"></script>'
    scores = score_passive(_page(html=html))
    wix = next(item for item in scores if item.name == "Wix")
    assert wix.points == 1
    assert confidence_for(set(wix.kinds)) == "low"


def test_unknown_site_has_no_scores() -> None:
    assert score_passive(_page(html="<html><p>hello</p></html>")) == []


def test_phpsessid_is_not_a_drupal_cookie() -> None:
    scores = score_passive(_page(set_cookie="PHPSESSID=abc"))
    assert all(item.name != "Drupal" for item in scores)


def test_drupal_sess_prefix_matches_session_cookie() -> None:
    scores = score_passive(_page(set_cookie="SESS1a2b3c=xyz"))
    drupal = next(item for item in scores if item.name == "Drupal")
    assert any(item.kind == "cookie" and item.value == "SESS" for item in drupal.evidence)


def test_choose_winner_tie_is_alphabetical() -> None:
    winner = choose_winner(
        [
            ScoredCms(name="Ghost", points=3, kinds=frozenset({"meta_generator"})),
            ScoredCms(name="Drupal", points=3, kinds=frozenset({"meta_generator"})),
        ]
    )
    assert winner is not None
    assert winner.name == "Drupal"


def test_choose_winner_prefers_higher_points() -> None:
    scores = score_passive(
        _page(
            html='<meta name="generator" content="WordPress 6.4"><script src="https://cdn.shopify.com/x.js"></script>',
            headers={"x-shopid": "9"},
        )
    )
    winner = choose_winner(scores)
    assert winner is not None
    assert winner.name == "Shopify"


def test_drupal_generator_scores() -> None:
    html = '<meta name="generator" content="Drupal 10">'
    scores = score_passive(_page(html=html))
    drupal = next(item for item in scores if item.name == "Drupal")
    assert drupal.version == "10"
    assert confidence_for(set(drupal.kinds)) == "medium"


def test_probe_requires_snippet_not_bare_200() -> None:
    generic = FetchResult(
        url="https://target.example/wp-admin/",
        ok=True,
        error="",
        status=200,
        headers={},
        set_cookie="",
        html="<html>home</html>",
        body="<html>home</html>",
    )
    probe = PathProbe("/wp-admin/", must_contain=("wordpress", "wp-admin"))
    assert probe_matches(generic, probe) is False
    hit = FetchResult(
        url="https://target.example/wp-admin/",
        ok=True,
        error="",
        status=200,
        headers={},
        set_cookie="",
        html="<html>wp-admin wordpress</html>",
        body="<html>wp-admin wordpress</html>",
    )
    assert probe_matches(hit, probe) is True


def test_default_mode_skips_active_paths() -> None:
    homepage = FetchResult(
        url="https://blog.example/",
        ok=True,
        error="",
        status=200,
        headers={},
        set_cookie="wordpress_test=1",
        html="<html></html>",
        body="<html></html>",
    )
    requested: list[str] = []

    def fake_fetch(url: str, *, delay: float, retries: int, timeout: float) -> FetchResult:
        requested.append(url)
        return FetchResult(
            url=url,
            ok=True,
            error="",
            status=200,
            headers={},
            set_cookie="",
            html="WordPress 6.3 readme",
            body="WordPress 6.3 readme",
        )

    result = run_detection(homepage, active=False, fetch_path=fake_fetch)
    assert result.cms == "WordPress"
    assert all("/wp-login.php" not in url for url in requested)
    assert any(url.endswith("/readme.html") for url in requested)
    assert result.version == "6.3"


def test_active_mode_requests_login_path() -> None:
    homepage = FetchResult(
        url="https://blog.example/",
        ok=True,
        error="",
        status=200,
        headers={},
        set_cookie="wordpress_test=1",
        html="<html></html>",
        body="<html></html>",
    )
    requested: list[str] = []

    def fake_fetch(url: str, *, delay: float, retries: int, timeout: float) -> FetchResult:
        requested.append(url)
        body = "wordpress wp-login" if url.endswith("/wp-login.php") else "WordPress"
        return FetchResult(
            url=url,
            ok=True,
            error="",
            status=200,
            headers={},
            set_cookie="",
            html=body,
            body=body,
        )

    result = run_detection(homepage, active=True, fetch_path=fake_fetch)
    assert any(url.endswith("/wp-login.php") for url in requested)
    assert result.cms == "WordPress"


def test_homepage_medium_with_version_skips_confirm_fetch() -> None:
    homepage = FetchResult(
        url="https://blog.example/",
        ok=True,
        error="",
        status=200,
        headers={},
        set_cookie="",
        html='<meta name="generator" content="WordPress 6.4.2">',
        body='<meta name="generator" content="WordPress 6.4.2">',
    )
    requested: list[str] = []

    def fake_fetch(url: str, *, delay: float, retries: int, timeout: float) -> FetchResult:
        requested.append(url)
        raise AssertionError("should not fetch")

    result = run_detection(homepage, active=False, fetch_path=fake_fetch)
    assert requested == []
    assert result.cms == "WordPress"
    assert result.version == "6.4.2"
    assert result.confidence == "medium"


def test_default_mode_does_not_probe_when_homepage_is_quiet() -> None:
    homepage = FetchResult(
        url="https://hardened.example/",
        ok=True,
        error="",
        status=200,
        headers={},
        set_cookie="",
        html="<html></html>",
        body="<html></html>",
    )
    requested: list[str] = []

    def fake_fetch(url: str, *, delay: float, retries: int, timeout: float) -> FetchResult:
        requested.append(url)
        raise AssertionError("default mode must not probe without a homepage score")

    result = run_detection(homepage, active=False, fetch_path=fake_fetch)
    assert requested == []
    assert result.cms is None


def test_active_mode_probes_catalogue_when_homepage_is_quiet() -> None:
    homepage = FetchResult(
        url="https://hardened.example/",
        ok=True,
        error="",
        status=200,
        headers={},
        set_cookie="",
        html="<html></html>",
        body="<html></html>",
    )
    requested: list[str] = []

    def fake_fetch(url: str, *, delay: float, retries: int, timeout: float) -> FetchResult:
        requested.append(url)
        if url.endswith("/readme.html"):
            return FetchResult(
                url=url,
                ok=True,
                error="",
                status=200,
                headers={},
                set_cookie="",
                html="WordPress 6.4 readme",
                body="WordPress 6.4 readme",
            )
        return FetchResult(
            url=url,
            ok=True,
            error="",
            status=200,
            headers={},
            set_cookie="",
            html="generic",
            body="generic",
        )

    result = run_detection(homepage, active=True, fetch_path=fake_fetch)
    assert any(url.endswith("/readme.html") for url in requested)
    assert result.cms == "WordPress"
    assert result.version == "6.4"
