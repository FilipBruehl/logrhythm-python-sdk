# SPEC-002 — Configuration

| Field | Value |
|---|---|
| ID | SPEC-002 |
| Status | Draft |
| Phase | A.2.3 |
| Component | Configuration |
| Depends on | [SPEC-000](design-principles.md), [SPEC-001](sdk-client.md) |
| Implementation | Not implemented |

## Status

Draft — target architecture only, not implemented. This specification has not yet
been reviewed against the [Review Criteria](README.md#review-criteria) in
[Design Specifications](README.md) and is not binding. No implementation may start
from this Draft; see the status model in [Design Specifications](README.md). Several
questions this specification would normally answer are, deliberately, left open —
see [Open Questions](#open-questions).

## Purpose

`Configuration` is the SDK's representation of resolved, validated settings. It gives
`LogRhythmClient` (see [SPEC-001](sdk-client.md)) — and, through it, the shared
infrastructure `LogRhythmClient` creates — a single, consistent, already-validated
source of truth for how the SDK should behave, instead of each component reading its
own settings from scattered or ambient sources.

Consistent with [SPEC-000](design-principles.md):

- `Configuration` centrally represents SDK-wide settings.
- It provides already-validated values to the components that need them.
- It performs no network access itself.
- It owns no resources requiring lifecycle management.
- It contains no API-specific business logic — API-specific settings are out of
  scope for this specification (see [Non-Goals](#non-goals)).

## Scope

**In scope:**

- The role and responsibilities of the `Configuration` component.
- Its conceptual public and internal surface.
- The kinds of sources it may resolve values from, and which are bindingly
  supported in version 1.
- How a resolved value's source relates to documented defaults, and what remains
  open should further sources be added later (see
  [Precedence and Merging](#precedence-and-merging)).
- The categories of validation it performs.
- That `Configuration` is immutable once created and validated (see
  [Immutability and Mutation](#immutability-and-mutation)).
- How it handles sensitive values.
- How it integrates with `LogRhythmClient` and `from_config(...)`.
- The categories of error it can produce.
- Its testability requirements.

**Out of scope** (referenced only; defined by their own future specifications):

- Authentication implementation details (how a credential is actually used to
  authenticate a request).
- TLS implementation details.
- HTTP transport implementation.
- Logging implementation.
- The SDK's exception hierarchy (exact exception class names/types).
- Concrete file parsers or file-format implementations.
- Concrete environment variable names.
- API-specific configuration (settings belonging to one API module rather than the
  SDK as a whole).

## Responsibilities

The `Configuration` component:

- represents the resolved SDK configuration as a single, coherent object.
- validates configuration values before they are considered usable (see
  [Validation](#validation)).
- provides consistent, already-validated values to the composition root
  (`LogRhythmClient`).
- keeps the origin of resolved values traceable at least at the level of source
  category (e.g. "this came from an explicit argument" vs. "this came from a
  documented default") — the concrete mechanism for this is not decided; see
  [Open Questions](#open-questions).
- handles sensitive values (e.g. credentials) safely throughout its own lifetime (see
  [Secrets](#secrets)).
- supports dependency injection and testing: it can be constructed directly, without
  going through any file, environment, or network-backed source (see
  [Testability](#testability)).

## Non-Responsibilities

The `Configuration` component:

- does not perform HTTP requests.
- does not authenticate.
- does not create a transport.
- does not configure API modules directly.
- contains no endpoint information.
- does not write files.
- does not mutate the process environment.
- loads nothing at import time (consistent with [SPEC-000](design-principles.md),
  "No side effects on import" / "No network access on import").
- manages no resources — it owns nothing that requires explicit release (see
  [Integration with LogRhythmClient](#integration-with-logrhythmclient)).

## Configuration Model

This section describes the resolved `Configuration` conceptually — as groups of
related settings, not as a Python class. At minimum, it separates:

- **General SDK settings** — behavior that applies across the SDK as a whole, not
  tied to a specific API module or shared-infrastructure concern.
- **Connection information** — inputs such as the target host and general connection
  behavior (e.g. timeouts), already anticipated at a high level in
  [Architecture Overview](../architecture/overview.md).
- **Authentication-related inputs** — the raw input(s) a future Authentication
  specification will need (e.g. a credential value). This specification defines only
  that `Configuration` has a structural place for such input, not how authentication
  itself works.
- **TLS-related inputs** — the raw input(s) a future TLS specification will need
  (e.g. which verification mode applies, an optional custom CA reference), matching
  the three modes already named in
  [Architecture Overview](../architecture/overview.md) (system trust store, custom
  CA, explicit opt-out). Again, only the structural place for this input is defined
  here, not TLS behavior itself.
- **Logging-related inputs** — the raw input(s) a future Logging specification will
  need (e.g. desired format or level). Only the structural place for this input is
  defined here, not logging behavior itself.

The exact fields within each group, their types, and their names are **not** decided
by this specification — they belong to `Configuration` itself and to the respective
future Authentication, TLS, and Logging specifications. No field names are invented
here.

## Public Interface

This section is conceptual only — no class definitions or method signatures with
types.

- **Direct creation.** A `Configuration` can be constructed directly, by supplying
  already-known values — the same way [SPEC-001](sdk-client.md) describes direct
  construction for `LogRhythmClient`.
- **Passing to `LogRhythmClient`.** A `Configuration` instance is what a caller
  supplies when directly constructing a `LogRhythmClient` (the dependency-injection
  path in [SPEC-001](sdk-client.md#construction)).
- **`from_config(...)` factory.** Decided: `from_config(...)` accepts a
  configuration file, or a path to one; loads it; validates it; builds a
  `Configuration` object from the result; and calls the primary constructor with
  that `Configuration` (see
  [Integration with LogRhythmClient](#integration-with-logrhythmclient)). Whether
  any additional factory or loader functions exist beyond `from_config(...)` — for
  example, one based on environment variables, should that become a supported
  source — is not decided; see [Open Questions](#open-questions).
- **Access to validated values.** Once resolved, consumers read already-validated
  values from the `Configuration` object. Because `Configuration` is immutable (see
  [Immutability and Mutation](#immutability-and-mutation)), those values cannot have
  changed since resolution. The exact access pattern is intentionally left
  unspecified at this conceptual level.

## Configuration Sources

For version 1, the following sources are **bindingly supported**:

1. **An already-constructed `Configuration` object.** Supplied directly by the
   caller to the primary constructor, e.g. via explicit Python arguments passed to
   `Configuration` itself (dependency injection; see
   [SPEC-001](sdk-client.md#dependency-injection)).
2. **A configuration file.** Loaded through `from_config(...)` (see
   [Integration with LogRhythmClient](#integration-with-logrhythmclient)).
3. **Documented defaults.** Applied for any value not supplied by (1) or (2); see
   [Defaults](#defaults).

**Environment variables are explicitly not a version 1 source.** They remain a
possible future extension (see
[Future Extensions](#future-extensions-non-binding)) and are not part of this
specification's binding scope.

[Architecture Overview](../architecture/overview.md) already names YAML, JSON, and
TOML as target file formats for configuration loading. This specification does not
re-decide that intent, but it also does not treat it as binding: which of these
formats `from_config(...)` actually supports, and the concrete loader mechanism, are
not finalized here — see [Open Questions](#open-questions). No concrete environment
variable names are defined by this specification.

## Precedence and Merging

Version 1's [Configuration Sources](#configuration-sources) decision narrows this
question considerably: a given `Configuration` is resolved from exactly **one**
active value-source at a time — either an already-constructed `Configuration` object
(built directly by the caller) or a configuration file loaded by `from_config(...)`
— plus documented defaults filling in anything the active source does not supply.
Version 1 does not combine an explicit `Configuration` object and a configuration
file within a single resolution.

Between that one active source and documented defaults, the order is not an open
design question: a value supplied by the active source always takes precedence over
a documented default, and a default only applies when the active source leaves a
value unset. This follows from what "default" means (see
[Defaults](#defaults)) and from
[SPEC-000](design-principles.md)'s "Explicit over implicit" and "No surprises"
principles — it is not a new or separately invented merge algorithm.

No existing document ([ADRs](../adr/README.md), [SPEC-000](design-principles.md),
[SPEC-001](sdk-client.md), [Architecture Overview](../architecture/overview.md), or
[Component Model](../architecture/components.md)) defines a precedence order beyond
this. In particular, how a possible future source (e.g. environment variables, see
[Future Extensions](#future-extensions-non-binding)) would combine with the sources
above — and in what order — is **not** decided and is out of scope for version 1; see
[Open Questions](#open-questions).

## Validation

- **When:** validation happens as part of resolving a `Configuration` — before it is
  considered usable and before it is handed to `LogRhythmClient` or any other
  component. This is Fail Fast behavior per [SPEC-000](design-principles.md): invalid
  configuration is rejected immediately, not discovered later during use.
- **No partially valid configuration:** a `Configuration` is either fully valid and
  usable, or resolution fails outright. A partially valid `Configuration` is never
  produced or handed onward.
- **No network validation:** validation never contacts LogRhythm or any other network
  endpoint.
- **No reachability checks:** validation never checks whether a configured host,
  path, or credential actually works against a real system.

This specification separates validation into four conceptual categories:

1. **Syntactic validation** — is a raw value well-formed on its own (e.g. is it a
   non-empty string of the expected kind)?
2. **Structural validation** — are the required settings present, and correctly
   shaped relative to the groups described in
   [Configuration Model](#configuration-model)?
3. **Semantic local validation** — do values make sense using only information
   available locally (e.g. a TLS verification mode is one of the known modes)? This
   still involves no network access.
4. **Runtime/server validation** — whether a value actually works against a real
   LogRhythm system (e.g. a credential is accepted, a host is reachable). This
   category is explicitly **not** performed by `Configuration`; it belongs to future
   Authentication/Transport specifications and happens only when the SDK is actually
   used, not during configuration resolution.

## Immutability and Mutation

**Decision: `Configuration` is immutable once it has been successfully created and
validated.** After that point, none of its values change for the lifetime of the
instance. This is a binding architectural decision, not an open question.

Reasoning:

- **Predictable behavior.** A `Configuration` instance may be held by
  `LogRhythmClient` and potentially referenced elsewhere. If it were mutable, any
  holder of a reference could change values another component is relying on, at any
  time, invisibly. Immutability guarantees that a `Configuration` observed once
  behaves the same way for as long as it exists — consistent with
  [SPEC-000](design-principles.md)'s "Explicit over implicit" and "No surprises"
  principles.
- **Thread safety.** Because an immutable `Configuration` has no mutable state after
  construction, concurrent reads from multiple threads are inherently safe — there
  is nothing to race on. This is a property of `Configuration` itself; it makes no
  claim about the thread-safety of `LogRhythmClient` or other shared components,
  which remains open elsewhere (see [SPEC-001](sdk-client.md#thread-safety)).
- **Simple testability.** A single `Configuration` instance can be constructed once
  and safely reused across multiple tests or assertions without risk of one test's
  use affecting another's, and without needing to guard against accidental mutation
  in test setup.
- **No unintended side effects.** Passing a `Configuration` into `LogRhythmClient`,
  an API module, or any other component can never have the side effect of changing
  what the caller — or any other holder of the same instance — sees.

Because a resolved `Configuration` never changes, obtaining a *different*
configuration (e.g. picking up an updated file) always means resolving a new
`Configuration` instance, not mutating the existing one. Whether the SDK offers any
convenience for that re-resolution (e.g. calling `from_config(...)` again) beyond
what is already described in this specification is not addressed here; dynamic,
in-place reloading of an existing instance is explicitly a
[Future Extension](#future-extensions-non-binding), not part of version 1.

## Secrets

- Secrets held in a `Configuration` must never be logged.
- Secrets must never appear in `repr()` or any other default string representation.
- Error messages must never contain secrets.
- Secrets must not be copied or serialized more than necessary to fulfill their
  purpose.
- Public documentation (this specification included) must never contain real
  secrets — only placeholders.

These follow directly from [SPEC-000](design-principles.md)'s security principles.
This specification does **not** decide how secrets are stored internally. Whether
`Configuration` integrates with any external secret-management system is explicitly
non-binding — see [Future Extensions](#future-extensions-non-binding) ("Secret
manager integration").

## Defaults

- Every default value must be documented; there are no undocumented, "just known"
  defaults.
- Defaults must be safe: where a choice must be made and no explicit value is given,
  the more secure option is the default, per
  [SPEC-000](design-principles.md#security-principles).
- Implicit, non-traceable defaults (a value that appears from nowhere with no
  documented origin) are not permitted.
- Security-relevant defaults must conform to [SPEC-000](design-principles.md). One
  such default is already decided elsewhere and applies here: TLS certificate
  verification defaults to enabled (see
  [Architecture Overview](../architecture/overview.md) and
  [SPEC-000](design-principles.md#security-principles)) — `Configuration`'s TLS-related
  inputs must reflect this rather than defaulting verification off.
- Beyond that one already-decided case, no other concrete default values (timeouts,
  log level, log format, etc.) are defined by this specification, because none are
  decided yet — see [Open Questions](#open-questions).

## Integration with LogRhythmClient

- **Direct construction — the primary constructor.** A caller constructs
  `LogRhythmClient` by passing an already-built `Configuration` instance directly:
  conceptually, `LogRhythmClient(configuration)`. This is the SDK's primary
  architectural mechanism, per [SPEC-001](sdk-client.md#construction). SPEC-002 only
  clarifies how `Configuration` specifically flows into it; the rest of that
  constructor's shape (e.g. `Logger` / `HTTP Transport` handling) is defined by
  [SPEC-001](sdk-client.md#construction) and is not repeated or changed here.
- **Usage by `from_config(...)`.** Decided: `from_config(...)` accepts a
  configuration file, or a path to one — not an already-built `Configuration`.
  Internally, it: (1) loads the file, (2) validates it, (3) constructs a
  `Configuration` object from the result, and (4) calls the primary constructor
  above with that `Configuration`. The exact file format(s) it accepts are not
  decided here — see [Open Questions](#open-questions).
- **`from_config(...)` remains a convenience factory, not a parallel architecture
  path.** Both variants — the primary constructor and `from_config(...)` — use the
  same underlying constructor internally; `from_config(...)` exists purely to save
  the caller from performing the load/validate/construct sequence themselves for the
  standard file-based case. It does not give `LogRhythmClient` a second, independent
  way to obtain a `Configuration` with different semantics.
- **Holding.** `LogRhythmClient`, as the composition root, holds the `Configuration`
  for as long as it is alive, per [SPEC-001](sdk-client.md#responsibilities).
- **No lifecycle resources.** `Configuration` holds no OS-level or network resources
  that require explicit release. [SPEC-001](sdk-client.md#resource-management) lists
  `Configuration` among the components `LogRhythmClient` may "manage," but for
  `Configuration` specifically that management has nothing to actually release —
  releasing a self-created `Configuration` is a no-op, unlike `Logger` or
  `HTTP Transport`, which may hold real resources.
- **Ownership rules are unchanged.** [SPEC-001](sdk-client.md#ownership)'s ownership
  rule applies to `Configuration` exactly as it applies to the other shared
  components: if `LogRhythmClient` created it, `LogRhythmClient` owns it; if it was
  injected by the caller, `LogRhythmClient` never takes ownership of it. This
  specification introduces no exception to that rule.

## Error Behaviour

This specification describes error categories conceptually. It does **not** define
exception class names or a class hierarchy — that belongs to a future
exception-handling specification, per [SPEC-001](sdk-client.md#public-api).

Categories of configuration error:

- **Missing required values** — a value the [Configuration Model](#configuration-model)
  requires is absent from every source that was consulted.
- **Invalid values** — a value is present but fails syntactic, structural, or local
  semantic validation (see [Validation](#validation)).
- **Conflicting values** — two settings that are documented as mutually exclusive
  are both provided within the same active source (see
  [Configuration Sources](#configuration-sources) and
  [Precedence and Merging](#precedence-and-merging)).
- **Unknown fields** — a source provides a field the
  [Configuration Model](#configuration-model) does not recognize. Whether this is
  rejected, ignored, or warned about is **not** decided — see
  [Open Questions](#open-questions).
- **Invalid combinations** — a combination of otherwise individually valid values
  that is structurally or semantically inconsistent.

In every category, resolution fails immediately and explicitly (Fail Fast, per
[SPEC-000](design-principles.md)) rather than producing a partially valid
`Configuration` or deferring the failure to later use.

## Testability

- `Configuration` can be fully tested without any network access, consistent with
  [SPEC-000](design-principles.md#testability).
- Tests can construct a `Configuration` directly, bypassing any file, environment, or
  other external source entirely.
- Testing `Configuration` must not depend on the real process environment — any
  future environment-variable-based source must be designed so tests can supply an
  isolated, fake environment mapping rather than mutating real process state.
- Any future loader or source implementation must be isolated and independently
  testable — swappable without needing the rest of the SDK, consistent with
  [SPEC-000](design-principles.md#architecture-principles) ("Stable abstractions").
- Secret redaction (see [Secrets](#secrets)) must itself be verifiable by a test —
  for example, that a `Configuration` containing a secret does not leak it via
  `repr()` or logging, without requiring the full future Logging implementation to
  exist first.
- Validation must be deterministic: the same inputs always produce the same
  validation result, independent of wall-clock time, network state, or execution
  order.
- Because a resolved `Configuration` is immutable (see
  [Immutability and Mutation](#immutability-and-mutation)), a single instance can be
  constructed once and reused across multiple tests or assertions without risk of
  one test's use affecting another's.

## Examples

Pseudocode only — illustrative of intended usage, not a committed API surface, not a
real implementation, and not a claim about any concrete field name or file format.
Placeholder values only; no real credentials.

**Direct `Configuration` creation:**

```python
configuration = Configuration(
    connection=...,  # e.g. host/timeout-related input; exact shape not decided
    authentication=...,  # raw input for a future Authentication specification
    tls=...,  # raw input for a future TLS specification
    logging=...,  # raw input for a future Logging specification
)
```

**Passing to `LogRhythmClient` (primary constructor):**

```python
client = LogRhythmClient(configuration)
```

The primary constructor also accepts `Logger` and `HTTP Transport` for dependency
injection, per [SPEC-001](sdk-client.md#construction) — not repeated here, since
their shape is not part of this specification.

**Using `from_config(...)` (convenience factory, loads a configuration file):**

```python
client = LogRhythmClient.from_config(config_path)
# `config_path` is a path to a configuration file. from_config(...) loads it,
# validates it, builds a Configuration, and calls the primary constructor above
# internally. The exact file format is an open question (see Open Questions).
```

**Dependency injection in tests:**

```python
test_configuration = Configuration(...)  # constructed directly, no file or env involved
client = LogRhythmClient(
    configuration=test_configuration,
    logger=fake_logger,
    transport=mock_transport,
)
```

## Open Questions

These are explicitly undecided. They must not be resolved silently by
implementation; each requires an explicit decision (and, where architecturally
significant, an ADR) before it can move out of this list.

- **File format.** Which file format(s) `from_config(...)` actually accepts —
  [Architecture Overview](../architecture/overview.md) names YAML, JSON, and TOML as
  targets, but this is not finalized at specification level.
- **Additional factory/loader methods.** Whether any factory or loader functions
  exist beyond the primary constructor and `from_config(...)` — for example, one
  based on environment variables, should that become a supported source — and what
  they would be called.
- **Unknown field handling.** Whether unknown fields from a source are rejected,
  ignored, or produce a warning (see [Error Behaviour](#error-behaviour)).
- **Relative path resolution.** Whether relative paths are supported in a
  configuration file path or within a configuration file's contents, and if so, what
  they are resolved relative to.
- **Concrete default values.** What the actual default values are for settings
  other than the one already decided (TLS verification on by default; see
  [Defaults](#defaults)).
- **Source traceability mechanism.** How (if at all) the origin of a resolved value
  is tracked or exposed (see [Responsibilities](#responsibilities)).

## Future Extensions (non-binding)

These are possible ideas for later, explicitly non-binding, and do not represent any
architectural decision or part of SPEC-002:

- Secret manager integration.
- Named configuration profiles.
- Multi-file / layered configuration.
- Dynamic reloading.
- Organization-wide policy defaults.
- Environment variables as a configuration source (see
  [Configuration Sources](#configuration-sources)).

## Non-Goals

This specification, and by extension the `Configuration` component itself,
explicitly does not cover:

- HTTP communication.
- Authentication logic.
- TLS implementation.
- Logging setup.
- Remote configuration retrieval.
- Dynamic reloading.
- A global `Configuration` singleton.
- API-specific settings.
- Invented vendor parameters.

## References

- [SPEC-000 — Design Principles](design-principles.md)
- [SPEC-001 — SDK Client](sdk-client.md)
- [Architecture Overview](../architecture/overview.md)
- [Component Model](../architecture/components.md)
- No existing ADR (see [docs/adr/](../adr/README.md)) is specific to configuration
  architecture; none is referenced here as directly applicable.
