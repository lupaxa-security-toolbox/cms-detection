"""lupaxa.cms_detection — identify a website CMS from public signals."""

from __future__ import annotations

from .api import detect, detect_many
from .exceptions import CmsDetectionError
from .models import DetectResult, Evidence
from .version import __version__, get_version

__all__ = [
    "CmsDetectionError",
    "DetectResult",
    "Evidence",
    "__version__",
    "detect",
    "detect_many",
    "get_version",
]
