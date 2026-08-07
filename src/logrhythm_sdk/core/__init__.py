"""Shared internal infrastructure for the LogRhythm SDK.

This subpackage holds logic shared across all LogRhythm API modules, such
as the exception hierarchy, transport, configuration, authentication, TLS
handling, and logging. It is an implementation detail: consumers import
from the stable public facades under ``logrhythm_sdk`` (for example,
:mod:`logrhythm_sdk.exceptions`), never from ``logrhythm_sdk.core`` directly.
Further components are added as they are implemented in later development
phases.
"""
