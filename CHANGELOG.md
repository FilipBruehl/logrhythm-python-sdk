# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
with Python-compatible version strings.

## [Unreleased]

### Added

- Configuration Foundation (SPEC-002): immutable resolved Pydantic models for the
  system endpoint, bearer credential, TLS and timeout settings, logging settings,
  and all seven API areas; plus an internal UTF-8 YAML/JSON/TOML loader with
  duplicate-key detection, source-aware path resolution, safe exception mapping,
  and credential-safe validation errors. The only new public surface is
  `logrhythm_sdk.configuration.Configuration`.
- Shared Pydantic model foundation (SPEC-008): immutable `SdkModel`,
  `RequestModel`, `ResponseModel`, and `InternalModel` bases with explicit alias
  handling, request/internal extra-field rejection, response extra-field
  retention, and reusable timezone-aware UTC normalization.
- Exception foundation (SPEC-007): the SDK's public exception hierarchy,
  rooted at `LogRhythmSdkError`, covering `ConfigurationError`,
  `ClientStateError` (including `ApiNotConfiguredError`, per SPEC-010),
  `TransportError`, `SerializationError`, `ModelError`, and `ApiError` with
  their minimum documented subclasses. Published from
  `logrhythm_sdk.exceptions`; `LogRhythmSdkError` is additionally re-exported
  from the package root. HTTP status mapping, vendor error body parsing,
  redaction integration, and third-party exception translation are not part
  of this change — they follow with the Transport and Logging layers.

### Changed

- Documentation and governance alignment for the Core Foundations phase:
  - established a central [Development Roadmap](docs/development/roadmap.md) with
    Phase A completion and the approved B.1.1-B.1.10 order (including B.1.4 as the
    next Logging Foundation step);
  - updated architecture and specification implementation-status documentation for
    implemented foundations (Configuration, Exceptions, Models);
  - integrated roadmap navigation into repository docs and updated AI coding-agent Git
    governance with explicit pre-action approval/safety rules.

### Deprecated

<!-- Add features scheduled for removal here. -->

### Removed

<!-- Add removed features here. -->

### Fixed

<!-- Add bug fixes here. -->

### Security

<!-- Add vulnerability fixes and security hardening here. -->

## [0.1.0] - 2026-08-06

### Added

- Initial repository foundation: `src`-layout package skeleton (`logrhythm_sdk`),
  project tooling configuration (Ruff, mypy, pytest, pytest-cov), documentation
  structure under `/docs`, and initial Architecture Decision Records. No functional
  API client, transport, or authentication yet.

[Unreleased]: https://github.com/FilipBruehl/logrhythm-python-sdk/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/FilipBruehl/logrhythm-python-sdk/releases/tag/v0.1.0
