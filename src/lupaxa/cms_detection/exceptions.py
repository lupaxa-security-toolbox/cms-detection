"""Errors raised by the public CMS detection API."""

from __future__ import annotations


class CmsDetectionError(Exception):
    """Invalid caller input (empty or unusable URL)."""
