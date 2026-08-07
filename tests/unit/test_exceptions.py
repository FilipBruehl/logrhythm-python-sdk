"""Tests for the LogRhythm SDK's exception hierarchy (SPEC-007 / SPEC-010)."""

from typing import Literal

import pytest

from logrhythm_sdk import exceptions
from logrhythm_sdk.exceptions import (
    ApiError,
    ApiNotConfiguredError,
    ApiValidationError,
    AuthenticationError,
    AuthorizationError,
    ClientClosedError,
    ClientInitializationError,
    ClientResponseError,
    ClientStateError,
    ConfigurationError,
    ConfigurationFormatError,
    ConfigurationSourceError,
    ConfigurationValidationError,
    ConflictError,
    LoggingConfigurationError,
    LogRhythmSdkError,
    ModelError,
    RateLimitError,
    RequestSerializationError,
    RequestValidationError,
    ResourceNotFoundError,
    ResponseDecodingError,
    ResponseValidationError,
    SerializationError,
    ServerResponseError,
    TransportConnectionError,
    TransportError,
    TransportProtocolError,
    TransportRequestError,
    TransportTimeoutError,
    TransportTlsError,
    UnexpectedRedirectError,
)

# Every public exception except the root, with its expected direct parent.
DIRECT_PARENT: dict[type[Exception], type[Exception]] = {
    ConfigurationError: LogRhythmSdkError,
    ConfigurationSourceError: ConfigurationError,
    ConfigurationFormatError: ConfigurationError,
    ConfigurationValidationError: ConfigurationError,
    LoggingConfigurationError: ConfigurationError,
    ClientStateError: LogRhythmSdkError,
    ClientInitializationError: ClientStateError,
    ClientClosedError: ClientStateError,
    ApiNotConfiguredError: ClientStateError,
    TransportError: LogRhythmSdkError,
    TransportConnectionError: TransportError,
    TransportTimeoutError: TransportError,
    TransportTlsError: TransportError,
    TransportProtocolError: TransportError,
    TransportRequestError: TransportError,
    SerializationError: LogRhythmSdkError,
    RequestSerializationError: SerializationError,
    ResponseDecodingError: SerializationError,
    ModelError: LogRhythmSdkError,
    RequestValidationError: ModelError,
    ResponseValidationError: ModelError,
    ApiError: LogRhythmSdkError,
    UnexpectedRedirectError: ApiError,
    ClientResponseError: ApiError,
    AuthenticationError: ClientResponseError,
    AuthorizationError: ClientResponseError,
    ResourceNotFoundError: ClientResponseError,
    ConflictError: ClientResponseError,
    RateLimitError: ClientResponseError,
    ApiValidationError: ClientResponseError,
    ServerResponseError: ApiError,
}

EXPECTED_PUBLIC_EXCEPTIONS: frozenset[type[Exception]] = frozenset(
    {LogRhythmSdkError, *DIRECT_PARENT}
)


# ---------------------------------------------------------------------------
# Hierarchy
# ---------------------------------------------------------------------------


def test_root_error_inherits_directly_from_exception() -> None:
    assert LogRhythmSdkError.__bases__ == (Exception,)


@pytest.mark.parametrize(
    ("exception_class", "expected_parent"),
    list(DIRECT_PARENT.items()),
    ids=lambda value: value.__name__,
)
def test_direct_parent(
    exception_class: type[LogRhythmSdkError], expected_parent: type[Exception]
) -> None:
    assert exception_class.__bases__ == (expected_parent,)


@pytest.mark.parametrize(
    "exception_class", list(EXPECTED_PUBLIC_EXCEPTIONS), ids=lambda value: value.__name__
)
def test_every_public_exception_is_a_logrhythm_sdk_error(
    exception_class: type[Exception],
) -> None:
    assert issubclass(exception_class, LogRhythmSdkError)


def test_api_not_configured_error_is_a_client_state_error() -> None:
    assert issubclass(ApiNotConfiguredError, ClientStateError)
    assert not issubclass(ApiNotConfiguredError, ConfigurationError)


# ---------------------------------------------------------------------------
# Catching
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "exception_class", list(EXPECTED_PUBLIC_EXCEPTIONS), ids=lambda value: value.__name__
)
def test_root_error_catches_every_sdk_exception(exception_class: type[Exception]) -> None:
    with pytest.raises(LogRhythmSdkError):
        _raise_minimal(exception_class)


def _raise_valueerror_past_an_sdk_except_clause() -> None:
    try:
        raise ValueError("not an SDK error")
    except LogRhythmSdkError:
        pytest.fail("LogRhythmSdkError must not catch unrelated builtin exceptions")


def test_root_error_does_not_catch_builtin_exceptions() -> None:
    with pytest.raises(ValueError, match="not an SDK error"):
        _raise_valueerror_past_an_sdk_except_clause()


def _raise_minimal(exception_class: type[Exception]) -> None:
    """Raise ``exception_class`` with the minimum arguments its constructor needs."""
    if exception_class is ApiNotConfiguredError:
        raise ApiNotConfiguredError(
            "not configured", api_name="search", configured=False, enabled=False, operation="list"
        )
    if exception_class is TransportTimeoutError:
        raise TransportTimeoutError("timed out", timeout_kind="connect")
    if issubclass(exception_class, ApiError):
        raise exception_class("api failure", http_status_code=500)
    raise exception_class("failure")


# ---------------------------------------------------------------------------
# Structured context: ApiNotConfiguredError
# ---------------------------------------------------------------------------


def test_api_not_configured_error_when_not_configured() -> None:
    error = ApiNotConfiguredError(
        "API area 'search' is not configured",
        api_name="search",
        configured=False,
        enabled=False,
        operation="list",
    )
    assert error.api_name == "search"
    assert error.configured is False
    assert error.enabled is False
    assert error.operation == "list"
    assert error.message == "API area 'search' is not configured"


def test_api_not_configured_error_when_explicitly_disabled() -> None:
    error = ApiNotConfiguredError(
        "API area 'search' is disabled",
        api_name="search",
        configured=True,
        enabled=False,
        operation="query",
    )
    assert error.configured is True
    assert error.enabled is False


# ---------------------------------------------------------------------------
# Structured context: TransportTimeoutError
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("timeout_kind", ["connect", "read", "write", "pool"])
def test_transport_timeout_error_records_timeout_kind(
    timeout_kind: Literal["connect", "read", "write", "pool"],
) -> None:
    error = TransportTimeoutError("timed out", timeout_kind=timeout_kind)
    assert error.timeout_kind == timeout_kind


# ---------------------------------------------------------------------------
# Structured context: ApiError
# ---------------------------------------------------------------------------


def test_api_error_required_field() -> None:
    error = ApiError("server error", http_status_code=500)
    assert error.http_status_code == 500
    assert error.vendor_status_code is None
    assert error.request_id is None
    assert error.server_request_id is None
    assert error.sanitized_endpoint is None
    assert error.safe_response_snippet is None


def test_api_error_optional_fields_are_independent_of_http_status_code() -> None:
    error = AuthenticationError(
        "authentication failed",
        http_status_code=401,
        vendor_status_code=40100,
        request_id="11111111-1111-1111-1111-111111111111",
        server_request_id="server-correlation-id",
        sanitized_endpoint="/admin/hosts",
        safe_response_snippet="<redacted excerpt>",
    )
    assert error.http_status_code == 401
    assert error.vendor_status_code == 40100
    assert error.http_status_code != error.vendor_status_code
    assert error.request_id == "11111111-1111-1111-1111-111111111111"
    assert error.server_request_id == "server-correlation-id"
    assert error.sanitized_endpoint == "/admin/hosts"
    assert error.safe_response_snippet == "<redacted excerpt>"


# ---------------------------------------------------------------------------
# Security: str() / repr()
# ---------------------------------------------------------------------------


def test_str_contains_only_the_message() -> None:
    error = LogRhythmSdkError("a safe, human-readable message")
    assert str(error) == "a safe, human-readable message"


def test_repr_does_not_leak_structured_fields() -> None:
    # A synthetic marker standing in for anything sensitive a structured field
    # might (incorrectly) be asked to hold. It is never passed to ``message``,
    # so a leak here would mean structured attributes are surfacing through the
    # default exception representation -- which they must not.
    secret_marker = "super-secret-test-token"
    error = ApiError(
        "authentication failed",
        http_status_code=401,
        sanitized_endpoint="/admin/hosts",
        safe_response_snippet=secret_marker,
    )
    assert secret_marker not in repr(error)
    assert secret_marker not in str(error)


def test_repr_of_context_carrying_error_contains_class_name_and_message() -> None:
    error = ApiNotConfiguredError(
        "API area 'search' is not configured",
        api_name="search",
        configured=False,
        enabled=False,
        operation="list",
    )
    # Deliberately does not assert an exact repr() string: CPython's choice of
    # single vs. double quotes for `repr(str)` is an implementation detail,
    # not an SDK contract. What the SDK actually guarantees is that the class
    # name and the message appear in repr(error).
    assert error.__class__.__name__ in repr(error)
    assert error.message in repr(error)


# ---------------------------------------------------------------------------
# Exception chaining
# ---------------------------------------------------------------------------


def _raise_transport_error_chained_from(underlying: ValueError) -> None:
    try:
        raise underlying
    except ValueError as caught:
        raise TransportConnectionError("connection failed") from caught


def test_chaining_preserves_cause() -> None:
    underlying = ValueError("some known underlying failure")
    with pytest.raises(TransportConnectionError) as excinfo:
        _raise_transport_error_chained_from(underlying)

    assert excinfo.value.__cause__ is underlying
    assert excinfo.value.__suppress_context__ is True


def _raise_transport_error_without_chaining(underlying: ValueError) -> None:
    try:
        raise underlying
    except ValueError:
        # Deliberately no `from` clause: confirms that plain Python exception
        # chaining (implicit `__context__`) is not disturbed by the SDK's
        # exception classes.
        raise TransportConnectionError("connection failed")  # noqa: B904


def test_implicit_context_is_recorded_without_explicit_chaining() -> None:
    underlying = ValueError("some known underlying failure")
    with pytest.raises(TransportConnectionError) as excinfo:
        _raise_transport_error_without_chaining(underlying)

    assert excinfo.value.__cause__ is None
    assert excinfo.value.__context__ is underlying


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def test_all_matches_the_expected_public_exception_set() -> None:
    assert set(exceptions.__all__) == {cls.__name__ for cls in EXPECTED_PUBLIC_EXCEPTIONS}


def test_all_has_no_duplicates_and_is_sorted() -> None:
    assert len(exceptions.__all__) == len(set(exceptions.__all__))
    assert exceptions.__all__ == sorted(exceptions.__all__)


@pytest.mark.parametrize(
    "exception_class", list(EXPECTED_PUBLIC_EXCEPTIONS), ids=lambda value: value.__name__
)
def test_every_public_exception_is_importable_from_the_facade(
    exception_class: type[Exception],
) -> None:
    assert getattr(exceptions, exception_class.__name__) is exception_class


def test_facade_does_not_export_anything_beyond_all() -> None:
    exported_names = {name for name in vars(exceptions) if not name.startswith("_")}
    # `exceptions` itself is not part of `__all__`; everything else public in the
    # module namespace must be.
    assert exported_names - set(exceptions.__all__) == set()
