# SPEC-001 — SDK Client

| Field | Value |
| --- | --- |
| ID | SPEC-001 |
| Status | Draft |
| Phase | A.2.2 |
| Component | SDK Client |
| Depends on | [SPEC-000](design-principles.md) |
| Implementation | Not implemented |

## Status

Draft. This specification has not yet been reviewed against the
[Review Criteria](README.md#review-criteria) in
[Design Specifications](README.md) and is not binding. No implementation may start
from this Draft; see the status model in [Design Specifications](README.md).

## Purpose

`LogRhythmClient` is the SDK's single public, high-level entry point and its
**composition root** — the one place where the shared infrastructure (configuration,
logging, transport) and the individual API modules — the seven API areas
[SPEC-010](api-modules.md#supported-apis) defines (Administration, AI Engine Cache
Drilldown, Metrics, AI Engine, Alarm, Case, and Search, in that implementation
order) — are assembled into a working object graph. Every other component either
is created and owned by `LogRhythmClient`, or is handed to it by the caller. This specification defines that role precisely: what
`LogRhythmClient` is responsible for, its public shape, how it obtains its
dependencies, who owns what, and how its lifecycle works. See
[Component Model](../architecture/components.md) for the diagram this specification
elaborates on.

## Scope

**In scope:**

- The responsibilities and non-responsibilities of `LogRhythmClient`.
- Its public surface at a conceptual level: construction, factory methods, context
  manager behavior, `close()`, and access to API modules.
- How it obtains shared infrastructure (creation vs. dependency injection).
- Ownership and lifecycle rules for the components it holds.

**Out of scope** (referenced only, defined by their own future specifications):

- The HTTP transport implementation.
- Authentication mechanics (e.g. how a bearer token is attached to a request).
- TLS behavior (trust store, custom CA, verification opt-out).
- Logging implementation and secret redaction.
- The SDK's exception hierarchy and error semantics.
- Configuration file formats (YAML/JSON/TOML) and their schema.
- Any concrete API module's endpoints, models, filters, or resources.

## Responsibilities

`LogRhythmClient`:

- is the SDK's public, high-level entry class.
- is the composition root: the one place the object graph is assembled.
- creates shared infrastructure (`Configuration`, `Logger`, `HTTP Transport`) when
  the caller does not supply it.
- accepts externally supplied shared infrastructure via dependency injection, as an
  alternative to creating it.
- injects the shared infrastructure — however obtained — into each API module.
- holds and manages the shared components for as long as the client is alive.
- manages the lifecycle of the resources it created internally.
- provides access to the configured API modules.

## Non-Responsibilities

`LogRhythmClient`:

- does not implement HTTP communication itself.
- does not authenticate itself.
- does not process or interpret API response data.
- contains no business logic.
- has no knowledge of individual endpoints.
- contains no API-specific logic — that lives exclusively in each API module (see
  [Component Model](../architecture/components.md)).

## Public API

This section describes the conceptual public surface only — no class definitions,
method signatures with types, or implementation.

- A **constructor** for direct construction: accepts already-built shared
  infrastructure, for the dependency-injection path.
- A **`from_config(...)` convenience factory method**: simplifies the standard case
  by building the required shared infrastructure internally and delegating to direct
  construction; it is not the primary architectural mechanism (see
  [Construction](#construction)).
- **Attribute-style access to each configured API module** (for example, the kind of
  `client.search` / `client.alarms` access already illustrated in
  [Architecture Overview](../architecture/overview.md)).
- A **`close()`** method that releases internally-owned resources.
- **Context manager support**, so `LogRhythmClient` can be used in a `with` block
  (see [Context Manager](#context-manager)).

Construction fails fast (per [SPEC-000](design-principles.md)) when required
configuration is missing or invalid; the specific exception type raised is defined by
a future specification, not this one.

## Construction

Two ways of obtaining a `LogRhythmClient` are in scope for this specification:

1. **Direct construction.** The caller passes already-built shared infrastructure
   (`Configuration`, `Logger`, `HTTP Transport`) directly. This is the
   dependency-injection path — and the **primary architectural mechanism** for
   obtaining a `LogRhythmClient`: see [Dependency Injection](#dependency-injection)
   and [Ownership](#ownership).
2. **`from_config(...)`.** A **convenience factory**, not an independent
   architectural mechanism. It accepts a configuration source, builds the required
   shared infrastructure internally, and then constructs the client the same way
   direct construction does. Its sole purpose is to simplify the standard case —
   callers who do not need to supply their own infrastructure — by handling that
   internal creation for them. The exact accepted input shape (an already-parsed
   configuration object, a file path, or something else) depends on a future
   Configuration specification and is not decided here.

`from_config(...)` does not replace or bypass direct construction: it is built on top
of it. Whenever a caller needs to supply a specific instance of a shared component
(for example, to inject a mock transport in tests), direct construction is used
instead of, or alongside, `from_config(...)`.

Additional factory methods (for example, constructing directly from a file path or
from environment variables) are **not** decided by this specification — see
[Open Questions](#open-questions) and [Future Extensions](#future-extensions-non-binding).

## Dependency Injection

- **Injectable:** `Configuration`, `Logger`, and `HTTP Transport` — the shared
  infrastructure components identified in
  [Component Model](../architecture/components.md) — can each be supplied by the
  caller instead of being created by `LogRhythmClient`.
- **Internally creatable:** the same three components can instead be created by
  `LogRhythmClient` itself, typically as part of `from_config(...)`.
- **When each is used:** direct construction via dependency injection is the primary
  architectural mechanism. `from_config(...)` is a convenience factory layered on top
  of it for the standard case, internally performing the same direct construction
  after building the required infrastructure. Explicit injection remains necessary
  whenever a caller needs a specific shared instance — for example, tests
  substituting a mock transport (see
  [SPEC-000, Testability](design-principles.md#testability)), or a host application
  that wants several components to share one logger or transport instance.

## Ownership

This is one of the most load-bearing rules in this specification and is stated
without room for interpretation, consistent with
[Component Model](../architecture/components.md):

- **If `LogRhythmClient` creates a shared component itself** (whether via direct
  construction or via the `from_config(...)` convenience factory), it has **full
  ownership** of that component and **full lifecycle responsibility** for it —
  including closing/releasing it when the client itself is closed.
- **If a shared component is injected by the caller** (the direct-construction /
  dependency-injection path), `LogRhythmClient` has **no ownership** of it. There is
  **no automatic cleanup**: `LogRhythmClient` never creates, closes, resets, or
  otherwise manages the lifecycle of a component it did not create. The caller
  remains solely responsible for that component's lifecycle, both before and after
  it is handed to the client.
- Ownership is decided **per component, at the time each component is obtained** —
  a client can simultaneously own some shared components (created by itself) and not
  own others (injected by the caller) at the same time.

## Lifecycle

- **Creation:** via direct construction or `from_config(...)` (see
  [Construction](#construction)). If construction fails partway through — for
  example, one shared component was already created internally before a later step
  fails — `LogRhythmClient` does not leak that partially created resource: anything
  it already created during a failed construction is released before the failure is
  reported to the caller. This follows directly from the Fail Fast and Explicit
  Resource Management principles in [SPEC-000](design-principles.md); it is not a new
  decision.
- **Usage:** once constructed, the client is expected to be used repeatedly —
  accessing any number of API modules, any number of times — for as long as it is
  open.
- **Closing:** `close()` releases only the shared components `LogRhythmClient` owns
  (see [Ownership](#ownership)). Injected components are left untouched.
- **Reuse:** whether a client can be used again after `close()` — reopened, or must
  be discarded and re-created — is **not decided**. See
  [Open Questions](#open-questions).
- **Error cases during use:** errors raised while calling into an API module (e.g. a
  failed HTTP request) are not part of this specification — see
  [Non-Goals](#non-goals) and the SDK's future exception-handling specification.

## Context Manager

`LogRhythmClient` is intended to support use as a context manager:

- Entering a `with` block yields the client itself, ready for use.
- Exiting the block — whether normally or due to an exception propagating out of it —
  calls `close()`.
- Closing via the context manager follows the same [Ownership](#ownership) rules as
  calling `close()` directly: only internally-owned resources are released; injected
  components are never touched.

This section describes intended behavior only; no implementation is specified here.

## Resource Management

- **Managed:** the shared infrastructure components (`Configuration`, `Logger`,
  `HTTP Transport`) that `LogRhythmClient` created itself.
- **Not managed:**
  - Shared infrastructure components supplied externally by the caller (see
    [Ownership](#ownership)).
  - The API module objects themselves — the seven API areas
    [SPEC-010](api-modules.md#supported-apis) defines — and anything inside them
    (each area's API Client and Resources, together with a resource's `resource.py`
    and whichever of `models/`, `filters/`, `sorting/`, and `options/` it uses; see
    [SPEC-010, Resource Hierarchy](api-modules.md#resource-hierarchy)) — per
    [Component Model](../architecture/components.md), these own no infrastructure of
    their own, so they hold nothing that needs closing independently of the shared
    infrastructure above.

## Thread Safety

No decision has been made about the thread-safety characteristics of
`LogRhythmClient` or the shared components it manages. This specification does not
assume or imply any particular thread-safety guarantee. See
[Open Questions](#open-questions).

## Examples

Pseudocode only — illustrative of intended usage, not a committed API surface or a
real implementation.

**Creating a client from configuration (convenience factory):**

```python
client = LogRhythmClient.from_config(some_configuration_source)
result = client.search.some_operation(...)
client.close()
```

**Context manager usage:**

```python
with LogRhythmClient.from_config(some_configuration_source) as client:
    result = client.alarms.some_operation(...)
# close() is called automatically on exit, releasing internally-owned resources only.
```

**Dependency injection (caller-supplied infrastructure):**

```python
client = LogRhythmClient(
    configuration=my_configuration,  # created and owned by the caller
    logger=my_logger,  # created and owned by the caller
    transport=my_mock_transport,  # e.g. a test double
)
# my_configuration / my_logger / my_mock_transport remain the caller's responsibility;
# client.close() will not close them.
```

## Open Questions

These are explicitly undecided. They must not be resolved silently by
implementation; each requires an explicit decision (and, where architecturally
significant, an ADR) before it can move out of this list.

- **Thread safety.** Whether `LogRhythmClient` and/or the shared components it
  manages are safe to use concurrently from multiple threads.
- **`close()` idempotency.** Whether calling `close()` more than once is safe (a
  no-op on subsequent calls) or an error.
- **Reuse after `close()`.** Whether a closed client can be reused/reopened, or must
  be discarded and replaced with a new instance.

Two questions previously listed here have since been settled or superseded by
later specifications and are tracked there instead, not duplicated here:
"additional factory methods beyond `from_config(...)`" is now
[SPEC-002](configuration.md#open-questions)'s "Additional factory/loader methods"
open question; "lazy vs. eager API module creation" is decided —
[SPEC-010](api-modules.md#lifecycle) establishes that every API client is
constructed eagerly.

## Future Extensions (non-binding)

These are possible ideas for later, explicitly non-binding, and do not represent any
architectural decision:

- An asynchronous client variant.
- A plugin system.
- Retry policies.
- Caching.

## Non-Goals

This specification, and by extension `LogRhythmClient` itself, explicitly does not
cover:

- HTTP implementation.
- Transport-level logic (connection handling, retries, timeouts).
- Authentication.
- Response parsing.
- API endpoints.
- Business logic.

## References

- [SPEC-000 — Design Principles](design-principles.md)
- [Architecture Overview](../architecture/overview.md)
- [Component Model](../architecture/components.md)
- [Design Specifications](README.md) — status model, review criteria, and change
  process this specification follows.
