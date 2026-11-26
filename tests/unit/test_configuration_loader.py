from __future__ import annotations

import json
from pathlib import Path

import pytest

from logrhythm_sdk.core.configuration import load_configuration
from logrhythm_sdk.exceptions import (
    ConfigurationFormatError,
    ConfigurationSourceError,
    ConfigurationValidationError,
    LoggingConfigurationError,
)


def _content(extension: str, *, token: str = "placeholder-token") -> str:
    if extension == ".json":
        return json.dumps(
            {
                "logrhythm": {
                    "base_url": "https://example.invalid",
                    "port": 8501,
                    "authentication": {"bearer_token": token},
                }
            }
        )
    if extension == ".toml":
        return f'''[logrhythm]
base_url = "https://example.invalid"
port = 8501

[logrhythm.authentication]
bearer_token = "{token}"
'''
    return f"""logrhythm:
  base_url: https://example.invalid
  port: 8501
  authentication:
    bearer_token: {token}
"""


@pytest.mark.parametrize("extension", [".yaml", ".yml", ".json", ".toml"])
def test_supported_file_formats_load(extension: str, tmp_path: Path) -> None:
    source = tmp_path / f"configuration{extension}"
    source.write_text(_content(extension), encoding="utf-8")

    configuration = load_configuration(source)

    assert configuration.logrhythm.base_url == "https://example.invalid"
    assert configuration.logrhythm.port == 8501


def test_utf8_is_read_explicitly(tmp_path: Path) -> None:
    source = tmp_path / "configuration.yaml"
    source.write_text(_content(".yaml", token="pläceholder-token"), encoding="utf-8")

    configuration = load_configuration(source)

    assert configuration.logrhythm.authentication.bearer_token.get_secret_value() == (
        "pläceholder-token"
    )


def test_missing_source_is_source_error(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationSourceError) as exc_info:
        load_configuration(tmp_path / "missing.yaml")

    assert isinstance(exc_info.value.__cause__, FileNotFoundError)


def test_directory_source_is_source_error(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationSourceError) as exc_info:
        load_configuration(tmp_path)

    assert isinstance(exc_info.value.__cause__, OSError)


def test_invalid_source_path_type_is_source_error() -> None:
    with pytest.raises(ConfigurationSourceError) as exc_info:
        load_configuration(None)  # type: ignore[arg-type]

    assert exc_info.value.__cause__ is None
    assert exc_info.value.__context__ is None


def test_unusable_source_path_string_is_source_error() -> None:
    with pytest.raises(ConfigurationSourceError) as exc_info:
        load_configuration("configuration\0.yaml")

    assert isinstance(exc_info.value.__cause__, ValueError)


def test_unsupported_extension_is_format_error(tmp_path: Path) -> None:
    source = tmp_path / "configuration.YAML"
    source.write_text(_content(".yaml"), encoding="utf-8")

    with pytest.raises(ConfigurationFormatError):
        load_configuration(source)


def test_invalid_utf8_is_format_error_without_parser_context(tmp_path: Path) -> None:
    source = tmp_path / "configuration.json"
    source.write_bytes(b"\xff\xfe")

    with pytest.raises(ConfigurationFormatError) as exc_info:
        load_configuration(source)

    assert exc_info.value.__cause__ is None
    assert exc_info.value.__context__ is None


@pytest.mark.parametrize("content", ["", "   \n"])
def test_empty_file_is_format_error(content: str, tmp_path: Path) -> None:
    source = tmp_path / "configuration.yaml"
    source.write_text(content, encoding="utf-8")

    with pytest.raises(ConfigurationFormatError):
        load_configuration(source)


@pytest.mark.parametrize(
    ("extension", "content"),
    [
        (".yaml", "logrhythm: ["),
        (".json", '{"logrhythm": '),
        (".toml", "[logrhythm\n"),
    ],
)
def test_invalid_syntax_is_format_error_without_parser_exception(
    extension: str, content: str, tmp_path: Path
) -> None:
    source = tmp_path / f"configuration{extension}"
    source.write_text(content, encoding="utf-8")

    with pytest.raises(ConfigurationFormatError) as exc_info:
        load_configuration(source)

    assert exc_info.value.__cause__ is None
    assert exc_info.value.__context__ is None


@pytest.mark.parametrize(
    ("extension", "content"),
    [
        (".yaml", "- first\n- second\n"),
        (".yaml", "null\n"),
        (".json", "[]"),
        (".json", "null"),
    ],
)
def test_non_mapping_root_is_format_error(extension: str, content: str, tmp_path: Path) -> None:
    source = tmp_path / f"configuration{extension}"
    source.write_text(content, encoding="utf-8")

    with pytest.raises(ConfigurationFormatError):
        load_configuration(source)


def test_non_string_root_key_is_validation_error(tmp_path: Path) -> None:
    source = tmp_path / "configuration.yaml"
    source.write_text("1: value\n", encoding="utf-8")

    with pytest.raises(ConfigurationValidationError) as exc_info:
        load_configuration(source)

    assert exc_info.value.__cause__ is None
    assert exc_info.value.__context__ is None


@pytest.mark.parametrize(
    ("extension", "content"),
    [
        (".json", '{"logrhythm": {"port": 1, "port": 2}}'),
        (
            ".yaml",
            "logrhythm:\n  port: 1\n  port: 2\n",
        ),
        (
            ".toml",
            "[logrhythm]\nport = 1\nport = 2\n",
        ),
    ],
)
def test_duplicate_keys_at_nested_level_are_format_errors(
    extension: str, content: str, tmp_path: Path
) -> None:
    source = tmp_path / f"configuration{extension}"
    source.write_text(content, encoding="utf-8")

    with pytest.raises(ConfigurationFormatError) as exc_info:
        load_configuration(source)

    assert exc_info.value.__cause__ is None
    assert exc_info.value.__context__ is None


def test_yaml_duplicate_detection_does_not_mutate_global_safe_loader(tmp_path: Path) -> None:
    import yaml  # type: ignore[import-untyped]

    source = tmp_path / "configuration.yaml"
    source.write_text("key: first\nkey: second\n", encoding="utf-8")

    with pytest.raises(ConfigurationFormatError):
        load_configuration(source)

    assert yaml.safe_load(source.read_text(encoding="utf-8")) == {"key": "second"}


def test_yaml_unhashable_mapping_key_is_format_error(tmp_path: Path) -> None:
    source = tmp_path / "configuration.yaml"
    source.write_text("? [one, two]\n: value\n", encoding="utf-8")

    with pytest.raises(ConfigurationFormatError) as exc_info:
        load_configuration(source)

    assert exc_info.value.__cause__ is None
    assert exc_info.value.__context__ is None


def test_file_paths_resolve_relative_to_source_directory(tmp_path: Path) -> None:
    source_directory = tmp_path / "configuration-directory"
    source_directory.mkdir()
    ca_bundle = source_directory / "certs" / "ca.pem"
    ca_bundle.parent.mkdir()
    ca_bundle.write_text("placeholder", encoding="utf-8")
    source = source_directory / "configuration.yaml"
    source.write_text(
        _content(".yaml")
        + "  tls:\n"
        + "    ca_bundle: certs/ca.pem\n"
        + "logging:\n"
        + "  file: logs/sdk.log\n",
        encoding="utf-8",
    )

    configuration = load_configuration(source)

    assert configuration.logrhythm.tls.ca_bundle == ca_bundle.resolve()
    assert configuration.logging.file == (source_directory / "logs" / "sdk.log").resolve()
    assert not (source_directory / "logs").exists()


def test_absolute_paths_loaded_from_file_remain_absolute(tmp_path: Path) -> None:
    ca_bundle = tmp_path / "ca.pem"
    ca_bundle.write_text("placeholder", encoding="utf-8")
    log_file = tmp_path / "sdk.log"
    source = tmp_path / "configuration.json"
    payload = json.loads(_content(".json"))
    payload["logrhythm"]["tls"] = {"ca_bundle": str(ca_bundle)}
    payload["logging"] = {"file": str(log_file)}
    source.write_text(json.dumps(payload), encoding="utf-8")

    configuration = load_configuration(source)

    assert configuration.logrhythm.tls.ca_bundle == ca_bundle
    assert configuration.logging.file == log_file


def test_file_schema_failure_uses_sanitized_validation_error(tmp_path: Path) -> None:
    secret_marker = "super-secret-test-marker"
    source = tmp_path / "configuration.json"
    payload = json.loads(_content(".json", token=secret_marker))
    payload["logrhythm"]["port"] = 0
    source.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ConfigurationValidationError) as exc_info:
        load_configuration(source)

    error = exc_info.value
    assert secret_marker not in str(error)
    assert secret_marker not in repr(error)
    assert secret_marker not in repr(error.__dict__)
    assert error.__cause__ is None
    assert error.__context__ is None


def test_input_bearing_parser_error_is_not_reachable(tmp_path: Path) -> None:
    secret_marker = "super-secret-test-marker"
    source = tmp_path / "configuration.json"
    source.write_text(f'{{"bearer_token": "{secret_marker}",', encoding="utf-8")

    with pytest.raises(ConfigurationFormatError) as exc_info:
        load_configuration(source)

    error = exc_info.value
    assert secret_marker not in str(error)
    assert secret_marker not in repr(error)
    assert secret_marker not in repr(error.__dict__)
    assert error.__cause__ is None
    assert error.__context__ is None


def test_loader_preserves_logging_specific_exception(tmp_path: Path) -> None:
    source = tmp_path / "configuration.json"
    payload = json.loads(_content(".json"))
    payload["logging"] = {"enabled": True}
    source.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(LoggingConfigurationError):
        load_configuration(source)
