"""CMS signature catalogue."""

from __future__ import annotations

from .models import CmsSignature, PathProbe

SIGNATURES: tuple[CmsSignature, ...] = (
    CmsSignature(
        name="BigCommerce",
        headers=("x-bc-apiversion",),
        scripts=("cdn.bc0a.com", "cdn11.bigcommerce.com"),
    ),
    CmsSignature(
        name="Blogger",
        meta_generator=("blogger",),
        scripts=("blogger.com", "blogspot.com"),
    ),
    CmsSignature(
        name="CMS Made Simple",
        meta_generator=("CMS Made Simple",),
        confirm_paths=(PathProbe("/doc/CHANGELOG.txt", must_contain=("CMS Made Simple",)),),
    ),
    CmsSignature(
        name="Concrete CMS",
        meta_generator=("concrete5", "concrete cms"),
        confirm_paths=(PathProbe("/concrete/js/build.js", must_contain=("concrete",)),),
        active_paths=(PathProbe("/concrete/themes/", must_contain=("concrete",)),),
    ),
    CmsSignature(
        name="Contao",
        meta_generator=("Contao",),
        confirm_paths=(PathProbe("/contao/", must_contain=("Contao",), allowed_status=(200, 302)),),
        active_paths=(PathProbe("/system/modules/", must_contain=("Contao",)),),
    ),
    CmsSignature(
        name="Craft CMS",
        meta_generator=("Craft CMS",),
        confirm_paths=(PathProbe("/cpresources/", must_contain=("Craft",)),),
        active_paths=(PathProbe("/admin", must_contain=("Craft",), allowed_status=(200, 302)),),
    ),
    CmsSignature(
        name="DotNetNuke (DNN)",
        meta_generator=("DotNetNuke", "DNN"),
        confirm_paths=(PathProbe("/DesktopModules/", must_contain=("DotNetNuke", "DNN")),),
        active_paths=(PathProbe("/Portals/", must_contain=("DotNetNuke", "Portal")),),
    ),
    CmsSignature(
        name="Drupal",
        cookies=("SESS",),
        meta_generator=("Drupal",),
        confirm_paths=(PathProbe("/misc/drupal.js", must_contain=("Drupal",)),),
        active_paths=(PathProbe("/sites/default/", must_contain=("Drupal",)),),
        version_patterns=(r"Drupal\s+([0-9]+(?:\.[0-9]+)*)",),
    ),
    CmsSignature(
        name="ExpressionEngine",
        meta_generator=("ExpressionEngine",),
        confirm_paths=(PathProbe("/system/expressionengine/", must_contain=("ExpressionEngine",)),),
        active_paths=(PathProbe("/themes/third_party/", must_contain=("ExpressionEngine",)),),
    ),
    CmsSignature(
        name="Ghost",
        meta_generator=("Ghost",),
        confirm_paths=(PathProbe("/ghost/api/admin/site/", must_contain=("ghost",)),),
        active_paths=(PathProbe("/ghost/", must_contain=("Ghost",), allowed_status=(200, 302)),),
        version_patterns=(r"Ghost\s+([0-9]+(?:\.[0-9]+)*)",),
    ),
    CmsSignature(
        name="HubSpot",
        meta_generator=("HubSpot",),
        scripts=("hs-scripts.com", "hsforms.net", "hubspot.net"),
    ),
    CmsSignature(
        name="Joomla",
        meta_generator=("Joomla!",),
        confirm_paths=(PathProbe("/media/system/js/core.js", must_contain=("Joomla",)),),
        active_paths=(
            PathProbe("/administrator/", must_contain=("Joomla",), allowed_status=(200, 302)),
        ),
        version_patterns=(r"Joomla!?\s+([0-9]+(?:\.[0-9]+)*)",),
    ),
    CmsSignature(
        name="Kentico",
        meta_generator=("Kentico",),
        confirm_paths=(PathProbe("/CMSPages/", must_contain=("Kentico",)),),
        active_paths=(PathProbe("/CMSWebParts/", must_contain=("Kentico",)),),
    ),
    CmsSignature(
        name="Magento",
        meta_generator=("Magento",),
        confirm_paths=(PathProbe("/js/mage", must_contain=("mage", "Magento")),),
        version_patterns=(r"Magento\s+([0-9]+(?:\.[0-9]+)*)",),
    ),
    CmsSignature(
        name="MODX",
        meta_generator=("MODX",),
        confirm_paths=(PathProbe("/assets/snippets/", must_contain=("MODX",)),),
        active_paths=(PathProbe("/manager/", must_contain=("MODX",), allowed_status=(200, 302)),),
    ),
    CmsSignature(
        name="October CMS",
        meta_generator=("October CMS",),
        confirm_paths=(PathProbe("/modules/system/assets/", must_contain=("October",)),),
    ),
    CmsSignature(
        name="phpBB",
        meta_generator=("phpBB",),
        confirm_paths=(
            PathProbe("/viewtopic.php", must_contain=("phpBB",)),
            PathProbe("/ucp.php", must_contain=("phpBB",), allowed_status=(200, 302)),
        ),
    ),
    CmsSignature(
        name="Plone",
        meta_generator=("Plone",),
        confirm_paths=(PathProbe("/@@login", must_contain=("Plone",), allowed_status=(200, 302)),),
        active_paths=(
            PathProbe("/login_form", must_contain=("Plone",), allowed_status=(200, 302)),
        ),
    ),
    CmsSignature(
        name="PrestaShop",
        meta_generator=("PrestaShop",),
        confirm_paths=(PathProbe("/themes/prestashop", must_contain=("PrestaShop",)),),
    ),
    CmsSignature(
        name="Shopify",
        headers=("x-shopid", "x-shopify-stage"),
        scripts=("cdn.shopify.com",),
    ),
    CmsSignature(
        name="Sitecore",
        meta_generator=("Sitecore",),
        confirm_paths=(PathProbe("/-/media/", must_contain=("Sitecore",)),),
        active_paths=(
            PathProbe("/sitecore/login", must_contain=("Sitecore",), allowed_status=(200, 302)),
        ),
    ),
    CmsSignature(
        name="Squarespace",
        headers=("x-squarespace-cache",),
        scripts=("static.squarespace.com",),
    ),
    CmsSignature(
        name="Textpattern",
        meta_generator=("Textpattern",),
        confirm_paths=(PathProbe("/textpattern/", must_contain=("Textpattern",)),),
        active_paths=(PathProbe("/rpc/", must_contain=("Textpattern",)),),
    ),
    CmsSignature(
        name="TYPO3",
        meta_generator=("TYPO3",),
        confirm_paths=(
            PathProbe("/typo3conf/", must_contain=("TYPO3",)),
            PathProbe("/typo3temp/", must_contain=("TYPO3",)),
        ),
        active_paths=(PathProbe("/typo3/", must_contain=("TYPO3",), allowed_status=(200, 302)),),
    ),
    CmsSignature(
        name="Umbraco",
        meta_generator=("Umbraco",),
        confirm_paths=(
            PathProbe("/umbraco/", must_contain=("Umbraco",), allowed_status=(200, 302)),
        ),
        active_paths=(PathProbe("/scripts/umbraco/", must_contain=("Umbraco",)),),
    ),
    CmsSignature(
        name="Webflow",
        meta_generator=("Webflow",),
        scripts=("webflow.com",),
    ),
    CmsSignature(
        name="Weebly",
        scripts=("weeblycloud.com", "weebly.com"),
    ),
    CmsSignature(
        name="Wix",
        meta_generator=("Wix.com",),
        scripts=("static.parastorage.com",),
    ),
    CmsSignature(
        name="WordPress",
        cookies=("wordpress_", "wp-settings-", "wordpress_logged_in_"),
        meta_generator=("WordPress",),
        confirm_paths=(
            PathProbe("/readme.html", must_contain=("WordPress",)),
            PathProbe("/wp-includes/wlwmanifest.xml", must_contain=("wlwmanifest",)),
        ),
        active_paths=(
            PathProbe(
                "/wp-login.php",
                must_contain=("wp-login", "wordpress"),
                allowed_status=(200, 302),
            ),
            PathProbe(
                "/wp-admin/",
                must_contain=("wp-admin", "wordpress"),
                allowed_status=(200, 302),
            ),
            PathProbe("/wp-content/", must_contain=("wp-content",), allowed_status=(200, 403)),
        ),
        version_patterns=(r"WordPress\s+([0-9]+(?:\.[0-9]+)*)",),
    ),
)


def signature_names() -> tuple[str, ...]:
    """Return CMS names in catalogue order."""
    return tuple(sig.name for sig in SIGNATURES)
