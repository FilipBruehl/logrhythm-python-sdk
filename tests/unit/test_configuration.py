from __future__ import annotations

from collections.abc import Mapping
from math import inf, nan
from pathlib import Path
from typing import IO, Any

import pytest
from pydantic import SecretStr, ValidationError

import logrhythm_sdk
import logrhythm_sdk.configuration as configuration_facade
from logrhythm_sdk.configuration import Configuration
from logrhythm_sdk.core.configuration import models
from logrhythm_sdk.core.models import InternalModel
from logrhythm_sdk.exceptions import (
    ConfigurationValidationError,
    LoggingConfigurationError,
)

API_AREAS = ("admin", "drilldown", "metrics", "aie", "alarms", "cases", "search")


def _valid_input(**overrides: object) -> dict[str, object]:
    data: dict[str, object] = {
        "logrhythm": {
            "base_url": "https://example.invalid",
            "port": 8501,
            "authentication": {"bearer_token": "placeholder-token"},
        }
    }
    data.update(overrides)
    return data


def _nested_mapping(data: dict[str, object], key: str) -> dict[str, object]:
    nested = data[key]
    assert isinstance(nested, dict)
    return nested


def test_configuration_is_the_only_public_configuration_export() -> None:
    assert configuration_facade.__all__ == ["Configuration"]
    assert configuration_facade.Configuration is Configuration
    assert not hasattr(logrhythm_sdk, "Configuration")
    for internal_name in (
        "ApiAreaSettings",
        "AuthenticationSettings",
        "LoggingSettings",
        "TimeoutSettings",
        "TlsSettings",
    ):
        assert not hasattr(configuration_facade, internal_name)
        assert not hasattr(logrhythm_sdk, internal_name)


@pytest.mark.parametrize(
    "model_class",
    [
        models.Configuration,
        models.LogRhythmSettings,
        models.AuthenticationSettings,
        models.TlsSettings,
        models.TimeoutSettings,
        models.LoggingSettings,
        models.LoggingRotationSettings,
        models.LoggingDebugSettings,
        models.ApiAreaSettings,
        models.ApiSettings,
    ],
)
def test_every_configuration_model_uses_internal_model(model_class: type[InternalModel]) -> None:
    assert issubclass(model_class, InternalModel)
    assert model_class.model_config["frozen"] is True
    assert model_class.model_config["extra"] == "forbid"
    assert model_class.model_config["hide_input_in_errors"] is True


def test_minimal_configuration_resolves_typed_defaults() -> None:
    configuration = Configuration(**_valid_input())

    assert isinstance(configuration.logrhythm, models.LogRhythmSettings)
    assert isinstance(configuration.logrhythm.authentication, models.AuthenticationSettings)
    assert isinstance(configuration.logrhythm.tls, models.TlsSettings)
    assert isinstance(configuration.logrhythm.timeouts, models.TimeoutSettings)
    assert isinstance(configuration.logging, models.LoggingSettings)
    assert isinstance(configuration.logging.rotation, models.LoggingRotationSettings)
    assert isinstance(configuration.logging.debug, models.LoggingDebugSettings)
    assert isinstance(configuration.apis, models.ApiSettings)
    assert configuration.logrhythm.tls.verify is True
    assert configuration.logrhythm.tls.ca_bundle is None
    assert configuration.logrhythm.timeouts.model_dump() == {
        "connect": 10.0,
        "read": 120.0,
        "write": 120.0,
        "pool": 10.0,
    }
    assert configuration.logging.level is models.LogLevel.INFO
    assert configuration.logging.format is models.LogFormat.TEXT
    assert configuration.logging.enabled is False
    assert configuration.logging.file is None
    assert configuration.logging.console is False
    assert configuration.logging.rotation.max_file_size_bytes == 10_485_760
    assert configuration.logging.rotation.backup_count == 5
    assert configuration.logging.debug.include_bodies is False
    assert configuration.logging.debug.max_body_size_bytes == 16_384


def test_configuration_graph_is_immutable() -> None:
    configuration = Configuration(**_valid_input())

    with pytest.raises(ValidationError):
        configuration.logrhythm.port = 443


@pytest.mark.parametrize(
    "data",
    [
        {"unexpected": True},
        {"logrhythm": {"unexpected": True}},
        {"logrhythm": {"authentication": {"unexpected": True}}},
        {"logging": {"rotation": {"unexpected": True}}},
        {"apis": {"unknown": {}}},
    ],
)
def test_unknown_fields_are_sanitized_validation_errors(data: dict[str, object]) -> None:
    valid_data = _valid_input()
    for key, value in data.items():
        if key in valid_data and isinstance(value, Mapping):
            target = _nested_mapping(valid_data, key)
            target.update(value)
        else:
            valid_data[key] = value

    with pytest.raises(ConfigurationValidationError):
        Configuration(**valid_data)


@pytest.mark.parametrize(
    "logrhythm",
    [
        {},
        {"base_url": "https://example.invalid"},
        {"base_url": "https://example.invalid", "port": 8501},
        {
            "base_url": "https://example.invalid",
            "port": 8501,
            "authentication": {},
        },
    ],
)
def test_required_values_are_enforced(logrhythm: dict[str, object]) -> None:
    with pytest.raises(ConfigurationValidationError):
        Configuration(logrhythm=logrhythm)


@pytest.mark.parametrize(
    "base_url",
    [
        "http://example.invalid",
        "ftp://example.invalid",
        "HTTPS://example.invalid",
        "https://",
        "https://user@example.invalid",
        "https://user:password@example.invalid",
        "https://valid-host:",
        "https://valid-host?",
        "https://valid-host#",
        "https://[2001:db8::1]:",
        "https://example.invalid:8501",
        "https://example.invalid:invalid",
        "https://example.invalid/",
        "https://example.invalid/api",
        "https://example.invalid?query=value",
        "https://example.invalid#fragment",
        "https://example.invalid path",
        "https://example.invalid\\path",
        "not-a-url",
    ],
)
def test_invalid_base_urls_are_rejected(base_url: str) -> None:
    data = _valid_input()
    _nested_mapping(data, "logrhythm")["base_url"] = base_url

    with pytest.raises(ConfigurationValidationError):
        Configuration(**data)


@pytest.mark.parametrize(
    "base_url",
    [
        "https://valid-host",
        "https://example.com",
        "https://192.0.2.1",
        "https://[2001:db8::1]",
    ],
)
def test_valid_base_url_is_preserved_without_normalization(base_url: str) -> None:
    data = _valid_input()
    _nested_mapping(data, "logrhythm")["base_url"] = base_url

    configuration = Configuration(**data)

    assert configuration.logrhythm.base_url == base_url
    assert configuration.logrhythm.port == 8501


def test_invalid_canonical_origin_does_not_expose_bearer_token() -> None:
    secret_marker = "canonical-origin-secret-marker"
    data = _valid_input()
    logrhythm = _nested_mapping(data, "logrhythm")
    logrhythm["base_url"] = "https://valid-host?"
    _nested_mapping(logrhythm, "authentication")["bearer_token"] = secret_marker

    with pytest.raises(ConfigurationValidationError) as exc_info:
        Configuration(**data)

    error = exc_info.value
    assert secret_marker not in str(error)
    assert secret_marker not in repr(error)
    assert error.__cause__ is None
    assert error.__context__ is None


@pytest.mark.parametrize("port", [0, -1, 65_536, "invalid", None])
def test_invalid_ports_are_rejected(port: object) -> None:
    data = _valid_input()
    _nested_mapping(data, "logrhythm")["port"] = port

    with pytest.raises(ConfigurationValidationError, match=r"logrhythm\.port"):
        Configuration(**data)


def test_bearer_token_uses_secret_str_and_is_redacted() -> None:
    secret_marker = "super-secret-test-marker"
    data = _valid_input()
    authentication = _nested_mapping(_nested_mapping(data, "logrhythm"), "authentication")
    authentication["bearer_token"] = secret_marker

    configuration = Configuration(**data)

    assert isinstance(configuration.logrhythm.authentication.bearer_token, SecretStr)
    assert secret_marker not in str(configuration)
    assert secret_marker not in repr(configuration)


def test_empty_bearer_token_is_rejected_by_sanitized_boundary() -> None:
    data = _valid_input()
    authentication = _nested_mapping(_nested_mapping(data, "logrhythm"), "authentication")
    authentication["bearer_token"] = ""

    with pytest.raises(ConfigurationValidationError, match="bearer_token") as exc_info:
        Configuration(**data)

    assert exc_info.value.__cause__ is None
    assert exc_info.value.__context__ is None


def test_programmatic_relative_paths_resolve_against_cwd(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    ca_bundle = tmp_path / "certs" / "ca.pem"
    ca_bundle.parent.mkdir()
    ca_bundle.write_text("placeholder", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    data = _valid_input(
        logging={"file": "logs/sdk.log"},
    )
    _nested_mapping(data, "logrhythm")["tls"] = {"ca_bundle": "certs/ca.pem"}

    configuration = Configuration(**data)

    assert configuration.logrhythm.tls.ca_bundle == ca_bundle.resolve()
    assert configuration.logging.file == (tmp_path / "logs" / "sdk.log").resolve()
    assert not (tmp_path / "logs").exists()


def test_nested_logging_model_is_resolved_at_configuration_boundary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    logging = models.LoggingSettings(file=Path("logs/sdk.log"))

    configuration = Configuration(**_valid_input(logging=logging))

    assert configuration.logging.file == (tmp_path / "logs" / "sdk.log").resolve()


def test_absolute_paths_remain_absolute(tmp_path: Path) -> None:
    ca_bundle = tmp_path / "ca.pem"
    ca_bundle.write_text("placeholder", encoding="utf-8")
    log_file = tmp_path / "sdk.log"
    data = _valid_input(logging={"file": log_file})
    _nested_mapping(data, "logrhythm")["tls"] = {"ca_bundle": ca_bundle}

    configuration = Configuration(**data)

    assert configuration.logrhythm.tls.ca_bundle == ca_bundle
    assert configuration.logging.file == log_file
    assert not log_file.exists()


def test_explicit_none_paths_remain_none() -> None:
    data = _valid_input(logging={"file": None})
    _nested_mapping(data, "logrhythm")["tls"] = {"ca_bundle": None}

    configuration = Configuration(**data)

    assert configuration.logrhythm.tls.ca_bundle is None
    assert configuration.logging.file is None


@pytest.mark.parametrize("ca_bundle_kind", ["missing", "directory"])
def test_ca_bundle_must_be_an_existing_file(tmp_path: Path, ca_bundle_kind: str) -> None:
    ca_bundle = tmp_path / ca_bundle_kind
    if ca_bundle_kind == "directory":
        ca_bundle.mkdir()
    data = _valid_input()
    _nested_mapping(data, "logrhythm")["tls"] = {"ca_bundle": ca_bundle}

    with pytest.raises(ConfigurationValidationError, match="ca_bundle"):
        Configuration(**data)


def test_ca_bundle_must_be_readable(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    ca_bundle = tmp_path / "ca.pem"
    ca_bundle.write_text("placeholder", encoding="utf-8")
    data = _valid_input()
    _nested_mapping(data, "logrhythm")["tls"] = {"ca_bundle": ca_bundle}
    original_open = Path.open

    def fail_for_ca_bundle(path: Path, *args: object, **kwargs: object) -> IO[Any]:
        if path == ca_bundle:
            raise PermissionError
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", fail_for_ca_bundle)

    with pytest.raises(ConfigurationValidationError, match="ca_bundle"):
        Configuration(**data)


@pytest.mark.parametrize("field", ["connect", "read", "write", "pool"])
@pytest.mark.parametrize("value", [0, -1, inf, -inf, nan, None])
def test_timeout_values_must_be_finite_and_positive(field: str, value: object) -> None:
    data = _valid_input()
    _nested_mapping(data, "logrhythm")["timeouts"] = {field: value}

    with pytest.raises(ConfigurationValidationError):
        Configuration(**data)


def test_timeout_overrides_are_resolved_independently() -> None:
    data = _valid_input()
    _nested_mapping(data, "logrhythm")["timeouts"] = {
        "connect": 1.5,
        "read": 600.0,
        "write": 30,
        "pool": 2.25,
    }

    configuration = Configuration(**data)

    assert configuration.logrhythm.timeouts.model_dump() == {
        "connect": 1.5,
        "read": 600.0,
        "write": 30.0,
        "pool": 2.25,
    }


@pytest.mark.parametrize("field", ["max_file_size_bytes", "max_body_size_bytes"])
def test_logging_size_limits_must_be_positive(field: str) -> None:
    section = "rotation" if field == "max_file_size_bytes" else "debug"
    data = _valid_input(logging={section: {field: 0}})

    with pytest.raises(ConfigurationValidationError):
        Configuration(**data)


@pytest.mark.parametrize("backup_count", [-1, "invalid", None])
def test_logging_backup_count_must_be_non_negative(backup_count: object) -> None:
    with pytest.raises(ConfigurationValidationError):
        Configuration(**_valid_input(logging={"rotation": {"backup_count": backup_count}}))


@pytest.mark.parametrize(("field", "value"), [("level", "TRACE"), ("format", "text")])
def test_logging_enums_accept_only_documented_values(field: str, value: str) -> None:
    with pytest.raises(ConfigurationValidationError):
        Configuration(**_valid_input(logging={field: value}))


def test_enabled_logging_requires_file_with_specific_exception() -> None:
    with pytest.raises(LoggingConfigurationError) as exc_info:
        Configuration(**_valid_input(logging={"enabled": True}))

    assert not isinstance(exc_info.value, ConfigurationValidationError)


def test_logging_exception_does_not_expose_bearer_token() -> None:
    secret_marker = "super-secret-test-marker"
    data = _valid_input(logging={"enabled": True})
    authentication = _nested_mapping(_nested_mapping(data, "logrhythm"), "authentication")
    authentication["bearer_token"] = secret_marker

    with pytest.raises(LoggingConfigurationError) as exc_info:
        Configuration(**data)

    error = exc_info.value
    assert secret_marker not in str(error)
    assert secret_marker not in repr(error)
    assert secret_marker not in repr(error.__dict__)
    assert error.__cause__ is None
    assert error.__context__ is None


@pytest.mark.parametrize("api_name", API_AREAS)
def test_every_api_area_is_resolved_and_disabled_by_default(api_name: str) -> None:
    configuration = Configuration(**_valid_input())

    api = getattr(configuration.apis, api_name)
    assert isinstance(api, models.ApiAreaSettings)
    assert api.enabled is False
    assert api.path is None


@pytest.mark.parametrize(
    ("settings", "valid"),
    [
        ({}, True),
        ({"enabled": False}, True),
        ({"enabled": False, "path": None}, True),
        ({"enabled": True}, True),
        ({"enabled": True, "path": None}, True),
        ({"enabled": True, "path": "foo/bar"}, True),
        ({"enabled": False, "path": "foo"}, False),
    ],
)
def test_api_enabled_path_state_matrix(settings: dict[str, object], valid: bool) -> None:
    data = _valid_input(apis={"admin": settings})

    if valid:
        configuration = Configuration(**data)
        assert configuration.apis.admin.enabled is settings.get("enabled", False)
        assert configuration.apis.admin.path == settings.get("path")
    else:
        with pytest.raises(ConfigurationValidationError):
            Configuration(**data)


@pytest.mark.parametrize(
    "path",
    [
        "",
        "/foo",
        "foo/",
        "foo//bar",
        ".",
        "..",
        "foo/../bar",
        "https://host/path",
        "foo?bar=1",
        "foo#fragment",
        "foo\\bar",
        "foo bar",
    ],
)
def test_invalid_api_paths_are_rejected(path: str) -> None:
    with pytest.raises(ConfigurationValidationError):
        Configuration(**_valid_input(apis={"search": {"enabled": True, "path": path}}))


@pytest.mark.parametrize("path", ["lr-admin-api", "foo", "foo/bar"])
def test_valid_api_paths_are_preserved(path: str) -> None:
    configuration = Configuration(**_valid_input(apis={"admin": {"enabled": True, "path": path}}))

    assert configuration.apis.admin.path == path


def test_validation_error_does_not_expose_secret_transitively() -> None:
    secret_marker = "super-secret-test-marker"
    data = _valid_input()
    logrhythm = _nested_mapping(data, "logrhythm")
    _nested_mapping(logrhythm, "authentication")["bearer_token"] = secret_marker
    logrhythm["port"] = 0

    with pytest.raises(ConfigurationValidationError) as exc_info:
        Configuration(**data)

    error = exc_info.value
    assert secret_marker not in str(error)
    assert secret_marker not in repr(error)
    assert secret_marker not in repr(error.__dict__)
    assert error.__cause__ is None
    assert error.__context__ is None


def test_unrecognized_field_name_is_not_reflected_in_error_message() -> None:
    secret_marker = "super-secret-test-marker"
    data = _valid_input()
    data[secret_marker] = True

    with pytest.raises(ConfigurationValidationError) as exc_info:
        Configuration(**data)

    assert secret_marker not in str(exc_info.value)


@pytest.mark.parametrize(
    "invalid_data",
    [
        {"logrhythm": "invalid"},
        {
            "logrhythm": {
                "base_url": "https://example.invalid",
                "port": 8501,
                "authentication": {"bearer_token": "placeholder-token"},
                "tls": "invalid",
            }
        },
        {**_valid_input(), "logging": "invalid"},
    ],
)
def test_non_mapping_model_sections_are_validation_errors(
    invalid_data: dict[str, object],
) -> None:
    with pytest.raises(ConfigurationValidationError):
        Configuration(**invalid_data)


@pytest.mark.parametrize("field", ["file", "ca_bundle"])
@pytest.mark.parametrize("value", ["", object()])
def test_invalid_filesystem_path_values_are_validation_errors(field: str, value: object) -> None:
    data = _valid_input()
    if field == "file":
        data["logging"] = {"file": value}
    else:
        _nested_mapping(data, "logrhythm")["tls"] = {"ca_bundle": value}

    with pytest.raises(ConfigurationValidationError) as exc_info:
        Configuration(**data)

    assert exc_info.value.__cause__ is None
    assert exc_info.value.__context__ is None
