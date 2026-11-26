"""LogRhythm SDK.

A typed Python SDK for the LogRhythm SIEM REST APIs.

This package is in an early foundation stage. The exception hierarchy,
shared model foundation, and configuration foundation are implemented;
API clients, authentication headers, transport, TLS runtime behavior, and
logging runtime behavior are added in later development phases.
"""

from logrhythm_sdk.exceptions import LogRhythmSdkError

__version__ = "0.1.0"

__all__ = ["LogRhythmSdkError", "__version__"]
