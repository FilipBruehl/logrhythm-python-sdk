"""The LogRhythm SDK's exception hierarchy.

Defines every exception class the SDK can raise, per
`SPEC-007 <../../../docs/specifications/exceptions.md>`_ (Exception Handling)
and the ``ApiNotConfiguredError`` addition from
`SPEC-010 <../../../docs/specifications/api-modules.md>`_ (API Modules). This
module is an implementation detail: consumers import from the stable public
facade, :mod:`logrhythm_sdk.exceptions`, never from here directly.
"""

from typing import Literal


class LogRhythmSdkError(Exception):
    """Root of every public SDK-raised exception.

    Every exception the LogRhythm Python SDK raises inherits, directly or
    indirectly, from this class. No public SDK exception exposes a
    third-party base class, so catching ``LogRhythmSdkError`` is sufficient
    to catch any SDK-raised failure. Exception messages are for humans only;
    callers must never parse this text to make decisions.

    Attributes:
        message: A human-readable description of the failure.

    Args:
        message: A human-readable description of the failure.
    """

    def __init__(self, message: str) -> None:
        """Initialize the error with its human-readable message."""
        super().__init__(message)
        self.message = message


# ---------------------------------------------------------------------------
# Configuration errors
# ---------------------------------------------------------------------------


class ConfigurationError(LogRhythmSdkError):
    """Base class for failures resolving or validating ``Configuration``."""


class ConfigurationSourceError(ConfigurationError):
    """A configuration source itself could not be used.

    For example, a file ``from_config(...)`` was pointed at could not be
    read.
    """


class ConfigurationFormatError(ConfigurationError):
    """A configuration source was readable but not parseable as expected."""


class ConfigurationValidationError(ConfigurationError):
    """A resolved configuration value failed validation."""


class LoggingConfigurationError(ConfigurationError):
    """SDK-owned logging is enabled but cannot be initialized.

    Raised when SDK-owned logging is enabled but its file path is missing,
    invalid, unwritable, or its handler cannot be initialized.
    """


# ---------------------------------------------------------------------------
# Client state errors
# ---------------------------------------------------------------------------


class ClientStateError(LogRhythmSdkError):
    """Base class for invalid use of ``LogRhythmClient`` itself.

    Covers invalid use independent of any particular request, as distinct
    from a failure that occurs while making one.
    """


class ClientInitializationError(ClientStateError):
    """``LogRhythmClient`` could not be constructed."""


class ClientClosedError(ClientStateError):
    """The client was used after being closed."""


class ApiNotConfiguredError(ClientStateError):
    """An API area was used while not configured or explicitly disabled.

    Both states use this same exception: the API area's entry may be
    entirely absent from ``Configuration`` (``configured=False``), or
    present but disabled (``configured=True``, ``enabled=False``). In either
    case, the API client and its namespace still exist, no network access
    occurs, and the failure is raised locally and immediately.

    Attributes:
        api_name: The name of the API area that was used (e.g. ``"search"``).
        configured: Whether the API area's entry is present in
            ``Configuration``.
        enabled: Whether the API area is enabled. Always ``False`` when this
            exception is raised.
        operation: The name of the operation the caller attempted.

    Args:
        message: A human-readable description of the failure.
        api_name: The name of the API area that was used.
        configured: Whether the API area's entry is present in
            ``Configuration``.
        enabled: Whether the API area is enabled.
        operation: The name of the operation the caller attempted.
    """

    def __init__(
        self,
        message: str,
        *,
        api_name: str,
        configured: bool,
        enabled: bool,
        operation: str,
    ) -> None:
        """Initialize the error with the API area's configuration state."""
        super().__init__(message)
        self.api_name = api_name
        self.configured = configured
        self.enabled = enabled
        self.operation = operation


# ---------------------------------------------------------------------------
# Transport errors
# ---------------------------------------------------------------------------


class TransportError(LogRhythmSdkError):
    """Base class for failures executing an HTTP request.

    Never raised for a well-formed response with an unexpected status; that
    is an ``ApiError`` (a response was actually received).
    """


class TransportConnectionError(TransportError):
    """A connection could not be established.

    For example, a DNS resolution failure or a refused connection.
    """


class TransportTimeoutError(TransportError):
    """A request exceeded one of Transport's timeout categories.

    A single class covers every timeout category; there are no separate
    public subclasses per category.

    Attributes:
        timeout_kind: Which timeout category elapsed.

    Args:
        message: A human-readable description of the failure.
        timeout_kind: Which timeout category elapsed.
    """

    def __init__(
        self,
        message: str,
        *,
        timeout_kind: Literal["connect", "read", "write", "pool"],
    ) -> None:
        """Initialize the error with which timeout category elapsed."""
        super().__init__(message)
        self.timeout_kind = timeout_kind


class TransportTlsError(TransportError):
    """A TLS handshake failed.

    Kept distinct from ``TransportConnectionError`` because it is a
    TLS-specific failure.
    """


class TransportProtocolError(TransportError):
    """The underlying HTTP exchange was malformed at the protocol level.

    Distinct from a well-formed response with an unexpected status
    (``ApiError``) or an unparseable JSON body (``SerializationError``).
    """


class TransportRequestError(TransportError):
    """The request could not be constructed or sent.

    Distinct from a failure that occurred once a connection already existed.
    """


# ---------------------------------------------------------------------------
# Serialization errors
# ---------------------------------------------------------------------------


class SerializationError(LogRhythmSdkError):
    """Base class for failures converting to or from the wire format."""


class RequestSerializationError(SerializationError):
    """An outgoing request body could not be serialized."""


class ResponseDecodingError(SerializationError):
    """A response body could not be decoded as expected.

    For example, invalid or malformed JSON where JSON was expected.
    """


# ---------------------------------------------------------------------------
# Model errors
# ---------------------------------------------------------------------------


class ModelError(LogRhythmSdkError):
    """Base class for failures converting between raw data and typed models."""


class RequestValidationError(ModelError):
    """Data the caller supplied fails local validation before being sent.

    Never raised for a problem in data that came back from the server; see
    ``ResponseValidationError`` for that case.
    """


class ResponseValidationError(ModelError):
    """Data LogRhythm returned fails validation against the expected model.

    Never raised for a problem in data the caller supplied; see
    ``RequestValidationError`` for that case.
    """


# ---------------------------------------------------------------------------
# API errors
# ---------------------------------------------------------------------------


class ApiError(LogRhythmSdkError):
    """Base class for errors where an HTTP response was actually received.

    Never raised for a connection-level or transport-level failure; those
    are a ``TransportError``. The HTTP status code alone is always
    sufficient to raise an appropriate ``ApiError`` -- a missing or invalid
    vendor error body never prevents this exception from being raised.

    Attributes:
        http_status_code: The HTTP status code of the received response.
        vendor_status_code: LogRhythm's own status code from its standard
            error body, if present. Tracked separately from
            ``http_status_code`` and never merged with it.
        request_id: The SDK-generated request ID for the failed request, if
            known.
        server_request_id: The server-supplied request or correlation ID,
            if LogRhythm returned one.
        sanitized_endpoint: The relative endpoint that was called, with any
            sensitive query parameters already redacted.
        safe_response_snippet: A redacted, size-limited excerpt of the
            response body, if available.

    Args:
        message: A human-readable description of the failure.
        http_status_code: The HTTP status code of the received response.
        vendor_status_code: LogRhythm's own status code, if present.
        request_id: The SDK-generated request ID, if known.
        server_request_id: The server-supplied request ID, if any.
        sanitized_endpoint: The relative endpoint that was called, already
            sanitized.
        safe_response_snippet: A redacted, size-limited excerpt of the
            response body, if available.
    """

    def __init__(
        self,
        message: str,
        *,
        http_status_code: int,
        vendor_status_code: int | None = None,
        request_id: str | None = None,
        server_request_id: str | None = None,
        sanitized_endpoint: str | None = None,
        safe_response_snippet: str | None = None,
    ) -> None:
        """Initialize the error with the received response's structured context."""
        super().__init__(message)
        self.http_status_code = http_status_code
        self.vendor_status_code = vendor_status_code
        self.request_id = request_id
        self.server_request_id = server_request_id
        self.sanitized_endpoint = sanitized_endpoint
        self.safe_response_snippet = safe_response_snippet


class UnexpectedRedirectError(ApiError):
    """A ``3xx`` response was received.

    Version 1 does not follow redirects by default, so a redirect response
    is not a normal outcome.
    """


class ClientResponseError(ApiError):
    """A ``4xx`` response without a more specific subclass below."""


class AuthenticationError(ClientResponseError):
    """A ``401`` response."""


class AuthorizationError(ClientResponseError):
    """A ``403`` response."""


class ResourceNotFoundError(ClientResponseError):
    """A ``404`` response."""


class ConflictError(ClientResponseError):
    """A ``409`` response."""


class RateLimitError(ClientResponseError):
    """A ``429`` response."""


class ApiValidationError(ClientResponseError):
    """A ``422`` response."""


class ServerResponseError(ApiError):
    """A ``5xx`` response."""
