"""Internal file loader for SDK configuration."""

from __future__ import annotations

import json
import tomllib
from collections.abc import Mapping
from pathlib import Path

import yaml  # type: ignore[import-untyped]
from yaml.constructor import ConstructorError  # type: ignore[import-untyped]
from yaml.nodes import MappingNode  # type: ignore[import-untyped]

from logrhythm_sdk.core.configuration.models import Configuration
from logrhythm_sdk.core.exceptions import (
    ConfigurationFormatError,
    ConfigurationSourceError,
)


class _DuplicateKeyError(ValueError):
    """Mark duplicate mapping keys without retaining their values."""


class _UniqueKeySafeLoader(yaml.SafeLoader):
    """Keep duplicate-key rejection local to configuration loading."""


def _construct_unique_mapping(
    loader: _UniqueKeySafeLoader, node: MappingNode, *, deep: bool = False
) -> dict[object, object]:
    loader.flatten_mapping(node)
    mapping: dict[object, object] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in mapping
        except TypeError:
            raise ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                "found an unhashable key",
                key_node.start_mark,
            ) from None
        if duplicate:
            raise _DuplicateKeyError
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_UniqueKeySafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


def load_configuration(path: str | Path) -> Configuration:
    """Load one UTF-8 YAML, JSON, or TOML file into Configuration.

    Args:
        path: The configuration file path.

    Returns:
        The immutable and resolved configuration.

    Raises:
        ConfigurationSourceError: If the source cannot be read.
        ConfigurationFormatError: If its format or parsed root is invalid.
        ConfigurationValidationError: If parsed values violate the schema.
        LoggingConfigurationError: If logging is enabled without a file path.
    """
    if not isinstance(path, (str, Path)):
        raise ConfigurationSourceError("The configuration source is invalid.")
    source = Path(path)

    source_error: OSError | ValueError | None = None
    decode_failed = False
    try:
        content = source.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        decode_failed = True
        content = ""
    except (OSError, ValueError) as error:
        source_error = error
        content = ""

    if source_error is not None:
        raise ConfigurationSourceError(
            "The configuration source could not be read."
        ) from source_error
    if decode_failed:
        raise ConfigurationFormatError("The configuration file is not valid UTF-8.") from None
    if not content.strip():
        raise ConfigurationFormatError("The configuration file is empty.")

    parsed = _parse_content(content, extension=source.suffix)
    if not isinstance(parsed, Mapping):
        raise ConfigurationFormatError("The configuration root must be a mapping.")
    return Configuration._from_mapping(parsed, base_path=source.resolve().parent)


def _parse_content(content: str, *, extension: str) -> object:
    parser_failed = False
    parsed: object = None
    try:
        if extension == ".json":
            parsed = json.loads(content, object_pairs_hook=_unique_json_object)
        elif extension in {".yaml", ".yml"}:
            parsed = yaml.load(content, Loader=_UniqueKeySafeLoader)
        elif extension == ".toml":
            parsed = tomllib.loads(content)
        else:
            raise ConfigurationFormatError("The configuration file extension is not supported.")
    except (json.JSONDecodeError, tomllib.TOMLDecodeError, yaml.YAMLError, _DuplicateKeyError):
        parser_failed = True

    if parser_failed:
        raise ConfigurationFormatError("The configuration file could not be parsed.") from None
    return parsed


def _unique_json_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKeyError
        result[key] = value
    return result
