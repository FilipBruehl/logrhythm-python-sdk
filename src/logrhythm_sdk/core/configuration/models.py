"""Resolved configuration models for the SDK."""

from __future__ import annotations

from collections.abc import Mapping
from enum import StrEnum
from pathlib import Path
from typing import Annotated, Any, Self
from urllib.parse import urlsplit

from pydantic import ConfigDict, Field, SecretStr, ValidationError, field_validator, model_validator

from logrhythm_sdk.core.exceptions import (
    ConfigurationValidationError,
    LoggingConfigurationError,
)
from logrhythm_sdk.core.models import InternalModel

_SAFE_FIELD_NAMES = frozenset(
    {
        "aie",
        "alarms",
        "admin",
        "apis",
        "authentication",
        "backup_count",
        "base_url",
        "bearer_token",
        "ca_bundle",
        "cases",
        "connect",
        "console",
        "debug",
        "drilldown",
        "enabled",
        "file",
        "format",
        "include_bodies",
        "level",
        "logging",
        "logrhythm",
        "max_body_size_bytes",
        "max_file_size_bytes",
        "metrics",
        "path",
        "pool",
        "port",
        "read",
        "rotation",
        "search",
        "timeouts",
        "tls",
        "verify",
        "write",
    }
)

type _Port = Annotated[int, Field(ge=1, le=65535)]
type _PositiveFloat = Annotated[float, Field(gt=0, allow_inf_nan=False)]
type _PositiveInt = Annotated[int, Field(gt=0)]
type _NonNegativeInt = Annotated[int, Field(ge=0)]


class _InvalidPathInputError(ValueError):
    """Mark a filesystem path that cannot be represented locally."""


class LogLevel(StrEnum):
    """Supported SDK logging levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogFormat(StrEnum):
    """Supported SDK logging output formats."""

    TEXT = "Text"
    JSON = "JSON"


class AuthenticationSettings(InternalModel):
    """Store the bearer credential used by the SDK."""

    model_config = ConfigDict(hide_input_in_errors=True)

    bearer_token: Annotated[SecretStr, Field(min_length=1)]


class TlsSettings(InternalModel):
    """Describe TLS verification and an optional custom trust source."""

    model_config = ConfigDict(hide_input_in_errors=True)

    verify: bool = True
    ca_bundle: Path | None = None

    @field_validator("ca_bundle")
    @classmethod
    def _validate_ca_bundle(cls, value: Path | None) -> Path | None:
        if value is None:
            return None
        if not value.is_absolute() or not value.exists() or not value.is_file():
            raise ValueError("CA bundle must be a readable file")
        try:
            with value.open("rb"):
                pass
        except OSError:
            raise ValueError("CA bundle must be a readable file") from None
        return value


class TimeoutSettings(InternalModel):
    """Store independent HTTP timeout categories in seconds."""

    model_config = ConfigDict(hide_input_in_errors=True)

    connect: _PositiveFloat = 10.0
    read: _PositiveFloat = 120.0
    write: _PositiveFloat = 120.0
    pool: _PositiveFloat = 10.0


class LogRhythmSettings(InternalModel):
    """Describe the single LogRhythm system used by all API areas."""

    model_config = ConfigDict(hide_input_in_errors=True)

    base_url: str
    port: _Port
    authentication: AuthenticationSettings
    tls: TlsSettings = Field(default_factory=TlsSettings)
    timeouts: TimeoutSettings = Field(default_factory=TimeoutSettings)

    @field_validator("base_url")
    @classmethod
    def _validate_base_url(cls, value: str) -> str:
        if not value.startswith("https://") or "\\" in value:
            raise ValueError("base URL must use HTTPS")
        invalid_url = False
        try:
            parsed = urlsplit(value)
            embedded_port = parsed.port is not None
        except ValueError:
            invalid_url = True
            parsed = urlsplit("")
            embedded_port = False
        if invalid_url:
            raise ValueError("base URL is invalid")
        if (
            parsed.scheme != "https"
            or parsed.hostname is None
            or embedded_port
            or parsed.netloc.endswith(":")
            or parsed.username is not None
            or parsed.password is not None
            or parsed.path
            or "?" in value
            or "#" in value
            or any(character.isspace() for character in value)
        ):
            raise ValueError("base URL must be a canonical HTTPS origin")
        return value


class LoggingRotationSettings(InternalModel):
    """Describe size-based SDK log rotation."""

    model_config = ConfigDict(hide_input_in_errors=True)

    max_file_size_bytes: _PositiveInt = 10_485_760
    backup_count: _NonNegativeInt = 5


class LoggingDebugSettings(InternalModel):
    """Describe explicitly enabled debug-body logging limits."""

    model_config = ConfigDict(hide_input_in_errors=True)

    include_bodies: bool = False
    max_body_size_bytes: _PositiveInt = 16_384


class LoggingSettings(InternalModel):
    """Describe the desired SDK-owned logging state."""

    model_config = ConfigDict(hide_input_in_errors=True)

    enabled: bool = False
    level: LogLevel = LogLevel.INFO
    format: LogFormat = LogFormat.TEXT
    file: Path | None = None
    console: bool = False
    rotation: LoggingRotationSettings = Field(default_factory=LoggingRotationSettings)
    debug: LoggingDebugSettings = Field(default_factory=LoggingDebugSettings)

    @model_validator(mode="after")
    def _require_file_when_enabled(self) -> Self:
        if self.enabled and self.file is None:
            raise LoggingConfigurationError("SDK logging requires a file path when enabled.")
        return self


class ApiAreaSettings(InternalModel):
    """Describe one API area's enablement and optional path override."""

    model_config = ConfigDict(hide_input_in_errors=True)

    enabled: bool = False
    path: str | None = None

    @field_validator("path")
    @classmethod
    def _validate_path(cls, value: str | None) -> str | None:
        if value is None:
            return None
        parsed = urlsplit(value)
        segments = value.split("/")
        if (
            not value
            or value.startswith("/")
            or value.endswith("/")
            or parsed.scheme
            or parsed.netloc
            or parsed.query
            or parsed.fragment
            or "\\" in value
            or any(character.isspace() for character in value)
            or any(segment in {"", ".", ".."} for segment in segments)
        ):
            raise ValueError("API path must be a non-empty relative path")
        return value

    @model_validator(mode="after")
    def _reject_path_for_disabled_area(self) -> Self:
        if not self.enabled and self.path is not None:
            raise ValueError("disabled API area cannot define a path override")
        return self


class ApiSettings(InternalModel):
    """Contain the seven explicitly supported API areas."""

    model_config = ConfigDict(hide_input_in_errors=True)

    admin: ApiAreaSettings = Field(default_factory=ApiAreaSettings)
    drilldown: ApiAreaSettings = Field(default_factory=ApiAreaSettings)
    metrics: ApiAreaSettings = Field(default_factory=ApiAreaSettings)
    aie: ApiAreaSettings = Field(default_factory=ApiAreaSettings)
    alarms: ApiAreaSettings = Field(default_factory=ApiAreaSettings)
    cases: ApiAreaSettings = Field(default_factory=ApiAreaSettings)
    search: ApiAreaSettings = Field(default_factory=ApiAreaSettings)


class Configuration(InternalModel):
    """Represent the immutable, validated, and resolved SDK configuration.

    Relative filesystem paths supplied directly are resolved against the current
    working directory at construction time. Recognized schema failures are exposed
    only as sanitized SDK configuration exceptions.
    """

    model_config = ConfigDict(hide_input_in_errors=True)

    logrhythm: LogRhythmSettings
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    apis: ApiSettings = Field(default_factory=ApiSettings)

    def __init__(self, **data: object) -> None:
        """Construct configuration from programmatic values.

        Args:
            **data: The nested configuration fields.
        """
        self._initialize(data, base_path=Path.cwd())

    @classmethod
    def _from_mapping(cls, data: Mapping[Any, object], *, base_path: Path) -> Self:
        """Construct configuration with an explicit source-relative base path."""
        instance = cls.__new__(cls)
        instance._initialize(data, base_path=base_path)
        return instance

    def _initialize(self, data: Mapping[Any, object], *, base_path: Path) -> None:
        invalid_path = False
        invalid_root_key = not all(isinstance(key, str) for key in data)
        safe_location: str | None = None
        validation_failed = False

        if not invalid_root_key:
            try:
                resolved_data = _resolve_filesystem_paths(data, base_path=base_path)
            except _InvalidPathInputError:
                invalid_path = True
                resolved_data = {}

        if not invalid_root_key and not invalid_path:
            try:
                super().__init__(**resolved_data)
            except ValidationError as error:
                validation_failed = True
                safe_location = _safe_error_location(error)

        if invalid_root_key or invalid_path or validation_failed:
            message = "Invalid configuration."
            if safe_location is not None:
                message = f"Invalid configuration at '{safe_location}'."
            raise ConfigurationValidationError(message) from None


def _safe_error_location(error: ValidationError) -> str | None:
    location = error.errors(include_url=False, include_context=False, include_input=False)[0].get(
        "loc"
    )
    safe_parts: list[str] = []
    for part in location:
        if not isinstance(part, str) or part not in _SAFE_FIELD_NAMES:
            break
        safe_parts.append(part)
    return ".".join(safe_parts) or None


def _resolve_filesystem_paths(data: Mapping[Any, object], *, base_path: Path) -> dict[str, object]:
    resolved = {str(key): value for key, value in data.items()}
    logrhythm = resolved.get("logrhythm")
    if isinstance(logrhythm, Mapping):
        resolved_logrhythm = dict(logrhythm)
        tls = resolved_logrhythm.get("tls")
        if isinstance(tls, Mapping):
            resolved_tls = dict(tls)
            if resolved_tls.get("ca_bundle") is not None:
                resolved_tls["ca_bundle"] = _resolve_path(
                    resolved_tls["ca_bundle"], base_path=base_path
                )
            resolved_logrhythm["tls"] = resolved_tls
        resolved["logrhythm"] = resolved_logrhythm

    logging = resolved.get("logging")
    if isinstance(logging, LoggingSettings):
        logging = logging.model_dump(mode="python")
    if isinstance(logging, Mapping):
        resolved_logging = dict(logging)
        if resolved_logging.get("file") is not None:
            resolved_logging["file"] = _resolve_path(resolved_logging["file"], base_path=base_path)
        resolved["logging"] = resolved_logging
    return resolved


def _resolve_path(value: object, *, base_path: Path) -> Path:
    if isinstance(value, str) and not value:
        raise _InvalidPathInputError
    try:
        path = Path(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        raise _InvalidPathInputError from None
    if not path.is_absolute():
        path = base_path / path
    return path.absolute()
