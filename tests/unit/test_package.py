"""Tests for the top-level ``logrhythm_sdk`` package."""

import importlib.metadata

import logrhythm_sdk


def test_package_is_importable() -> None:
    assert logrhythm_sdk is not None


def test_version_matches_project_metadata() -> None:
    installed_version = importlib.metadata.version("logrhythm-python-sdk")
    assert logrhythm_sdk.__version__ == installed_version


def test_public_exports_are_limited_to_version() -> None:
    assert logrhythm_sdk.__all__ == ["__version__"]
