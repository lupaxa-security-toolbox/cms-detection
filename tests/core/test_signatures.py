"""Signature catalogue ported from the proof of concept."""

from __future__ import annotations

from lupaxa.cms_detection.signatures import SIGNATURES, signature_names

POC_NAMES = (
    "BigCommerce",
    "Blogger",
    "CMS Made Simple",
    "Concrete CMS",
    "Contao",
    "Craft CMS",
    "DotNetNuke (DNN)",
    "Drupal",
    "ExpressionEngine",
    "Ghost",
    "HubSpot",
    "Joomla",
    "Kentico",
    "Magento",
    "MODX",
    "October CMS",
    "phpBB",
    "Plone",
    "PrestaShop",
    "Shopify",
    "Sitecore",
    "Squarespace",
    "Textpattern",
    "TYPO3",
    "Umbraco",
    "Webflow",
    "Weebly",
    "Wix",
    "WordPress",
)


def test_all_poc_names_present() -> None:
    assert signature_names() == POC_NAMES


def test_every_path_probe_has_must_contain() -> None:
    for sig in SIGNATURES:
        for probe in (*sig.confirm_paths, *sig.active_paths):
            assert probe.must_contain, f"{sig.name} {probe.path} missing must_contain"


def test_wordpress_login_is_active_not_confirm() -> None:
    wp = next(sig for sig in SIGNATURES if sig.name == "WordPress")
    confirm = {probe.path for probe in wp.confirm_paths}
    active = {probe.path for probe in wp.active_paths}
    assert "/readme.html" in confirm
    assert "/wp-login.php" in active
    assert "/wp-admin/" in active


def test_generic_shared_paths_are_not_confirm() -> None:
    forbidden = {"/modules/", "/static/", "/themes/", "/tmp/"}
    for sig in SIGNATURES:
        confirm = {probe.path for probe in sig.confirm_paths}
        assert not (confirm & forbidden), sig.name
