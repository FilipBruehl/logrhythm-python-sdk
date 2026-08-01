# 0005. Use Pydantic v2 for SDK models

## Status

Accepted

## Context

[SPEC-008 — Models](../specifications/models.md) requires a single, consistent way
to represent every request, response, and internal data structure in the SDK:
validated, immutable, strictly-typed models with explicit manufacturer field
aliasing (see [SPEC-008, Aliases](../specifications/models.md#aliases)) and a clear
split between strict outgoing validation and tolerant incoming validation (see
[SPEC-008, Request Models](../specifications/models.md#request-models) /
[Response Models](../specifications/models.md#response-models)). This needs to hold
uniformly across every API module's models and across `core` infrastructure's own
internal models (e.g. `RequestContext`, the SDK-internal response representation;
see [SPEC-008, Internal Models](../specifications/models.md#internal-models)) — a
mix of `dataclasses` for internal use and a validation library for public models
would fracture that consistency and duplicate validation logic across the codebase.

## Alternatives considered

- **`dataclasses` (standard library)** — no dependency, but no runtime validation,
  no built-in field aliasing, no immutability enforcement beyond `frozen=True`, and
  no JSON Schema generation. Would require hand-rolled validation for every model,
  contradicting [SPEC-000](../specifications/design-principles.md#implementation-principles)'s
  "No hidden magic" and "Readability over brevity" by pushing repetitive,
  error-prone validation code into every resource.
- **`attrs`** — mature and flexible, with validators and converters, but validation
  is opt-in and manual per field rather than declarative and centrally enforced; no
  first-party JSON Schema generation; strict/tolerant validation modes and
  manufacturer aliasing would again need to be built by hand.
- **Pydantic v1** — superseded by v2's rewritten, faster core (`pydantic-core`,
  compiled) and its overhauled validation/serialization model; starting a new
  project on v1 would mean adopting a design v2 has already succeeded.
- **A hand-rolled internal validation layer** — maximum control and zero
  dependency, but reimplements a large, well-tested surface (validation, coercion
  rules, error reporting, JSON Schema) that Pydantic already provides, for no
  architectural benefit specific to this SDK.

## Decision

The SDK uses **Pydantic v2, exclusively**, for every model — public and internal,
request and response — as already decided in
[SPEC-008 — Models](../specifications/models.md#purpose). No `dataclasses` and no
`attrs` are used anywhere in this architecture, including for `core`-internal data
structures. This accepts Pydantic as a runtime dependency deliberately: the
validation, immutability, aliasing, and serialization guarantees
[SPEC-008](../specifications/models.md) and
[SPEC-009](../specifications/filters-and-options.md) require are treated as
important enough to justify a runtime dependency, rather than avoided via a
lighter-weight, hand-built alternative.

## Consequences

- Pydantic v2 (and its compiled `pydantic-core` dependency) becomes a mandatory
  runtime dependency of the SDK — see [pyproject.toml](../../pyproject.toml).
- Every model in the SDK — including `core`-internal ones — gains a single,
  consistent validation, immutability, and serialization mechanism, exactly as
  [SPEC-008](../specifications/models.md#base-models) and
  [SPEC-009](../specifications/filters-and-options.md#base-models) already specify.
- The official Pydantic mypy plugin (`pydantic.mypy`) is enabled in
  [pyproject.toml](../../pyproject.toml), with `init_typed`, `init_forbid_extra`,
  and `warn_required_dynamic_aliases` set, so static type checking understands
  Pydantic's generated `__init__` and aliasing behavior correctly.
- Raising the SDK's minimum supported Pydantic version, or changing which Pydantic
  major version is supported, is itself a future decision, evaluated like any other
  dependency change — see
  [ADR Policy](../development/claude-workflow.md#architecture-governance) and
  [docs/adr/README.md](README.md#when-an-adr-is-required).
- A future move away from Pydantic, or introduction of a second modeling approach
  alongside it, would reverse this decision and requires its own ADR, per
  [docs/adr/README.md](README.md#when-an-adr-is-required).
