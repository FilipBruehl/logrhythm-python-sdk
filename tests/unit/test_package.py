"""Tests for the top-level ``logrhythm_sdk`` package."""

import importlib.metadata

import logrhythm_sdk
from logrhythm_sdk import exceptions


def test_package_is_importable() -> None:
    assert logrhythm_sdk is not None


def test_version_matches_project_metadata() -> None:
    installed_version = importlib.metadata.version("logrhythm-python-sdk")
    assert logrhythm_sdk.__version__ == installed_version


def test_public_exports_are_version_and_root_error() -> None:
    assert set(logrhythm_sdk.__all__) == {"__version__", "LogRhythmSdkError"}


def test_root_error_reexport_is_the_same_object_as_the_facade() -> None:
    assert logrhythm_sdk.LogRhythmSdkError is exceptions.LogRhythmSdkError
