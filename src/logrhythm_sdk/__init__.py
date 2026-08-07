"""LogRhythm SDK.

A typed Python SDK for the LogRhythm SIEM REST APIs.

This package is in an early foundation stage. The exception hierarchy
(SPEC-007) is implemented; API clients, authentication, transport, and
configuration handling are not yet implemented and are added in later
development phases.
"""

from logrhythm_sdk.exceptions import LogRhythmSdkError

__version__ = "0.1.0"

__all__ = ["LogRhythmSdkError", "__version__"]
