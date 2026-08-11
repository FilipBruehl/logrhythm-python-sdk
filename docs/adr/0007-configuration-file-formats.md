# 0007. Support YAML, JSON, and TOML configuration files

## Status

Accepted

## Context

[SPEC-002 — Configuration](../specifications/configuration.md#open-questions) left
the concrete configuration file format(s) `from_config(...)` accepts as an
explicitly open question, even though the
[Architecture Overview](../architecture/overview.md#planned-configuration) already
named YAML, JSON, and TOML as target formats without treating that as binding. A
binding decision is needed before `Configuration`'s file-loading path (see
[SPEC-002, Public and Internal Interface](../specifications/configuration.md#public-and-internal-interface))
can be implemented.

## Alternatives considered

- **YAML only** — the most common format for infrastructure/SDK configuration and
  comment-friendly, but forcing a single format would needlessly restrict
  operators who standardize on JSON or TOML elsewhere in their tooling.
- **A single, SDK-specific format or DSL** — rejected outright: it would add a
  bespoke parser to maintain and give operators nothing they can reuse from
  existing tooling, contradicting
  [SPEC-000](../specifications/design-principles.md#implementation-principles)'s
  "Readability over brevity" and "No hidden magic."
- **Automatic/heuristic format detection** (sniffing file content rather than
  reading the extension) — rejected: implicit and unpredictable, contrary to
  [SPEC-000](../specifications/design-principles.md#architecture-principles)'s
  "Explicit over implicit" principle; a file's format should be obvious from its
  name, not guessed from its bytes.
- **A third-party TOML library** (e.g. `tomli`) — unnecessary now that `tomllib`
  ships in the standard library for the SDK's Python 3.13 baseline
  ([ADR-0001](0001-python-313.md)); adding a dependency for functionality the
  standard library already provides would contradict keeping the dependency
  footprint minimal.
- **Converting between formats, or merging multiple files of different formats
  into one configuration** — out of scope;
  [SPEC-002](../specifications/configuration.md#configuration-sources) already
  resolves a `Configuration` from exactly one active source.

## Decision

Version 1 bindingly supports exactly three configuration file formats, closing
[SPEC-002](../specifications/configuration.md#open-questions)'s previously open
"File format" question:

- **YAML** (`.yaml`, `.yml`) — parsed via **PyYAML**, using only its safe-loading
  interface (e.g. `yaml.safe_load`); the full/unsafe loader is never used.
- **JSON** (`.json`) — parsed via the Python standard library's `json` module.
- **TOML** (`.toml`) — parsed via the Python standard library's **`tomllib`**
  (available for the SDK's Python 3.13+ baseline, per
  [ADR-0001](0001-python-313.md)). No additional third-party TOML library is
  added.

**Format is determined exclusively by file extension** (`.yaml`/`.yml`, `.json`,
`.toml`) — never by inspecting file content or any other heuristic. A file with an
unrecognized or unsupported extension is rejected; per
[SPEC-007 — Exception Handling](../specifications/exceptions.md#configuration-errors),
this is one of the cases surfaced as `ConfigurationFormatError`. No conversion
between formats is offered, and no format-detection fallback exists.

## Consequences

- **PyYAML** becomes a mandatory runtime dependency of the SDK — see
  [pyproject.toml](../../pyproject.toml). JSON and TOML support add no new runtime
  dependency, since both are covered by the Python 3.13 standard library.
- [SPEC-002 — Configuration](../specifications/configuration.md#configuration-sources)
  is updated in the same change as this ADR to record this as a binding decision
  rather than an open question.
- Only safe YAML loading is ever used, consistent with
  [SPEC-000](../specifications/design-principles.md#security-principles)'s
  "Prefer secure defaults" — arbitrary Python object construction via YAML tags is
  never possible through `from_config(...)`.
- Adding a fourth configuration format, changing the extension-based detection
  rule, or introducing content-based format detection would reverse this decision
  and requires its own ADR, per [docs/adr/README.md](README.md#when-an-adr-is-required).
