# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
with Python-compatible version strings.

## [Unreleased]

### Added

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

<!-- Add changes to existing behavior here. -->

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
