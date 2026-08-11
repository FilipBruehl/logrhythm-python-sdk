# SPEC-006 — Logging

| Field | Value |
| --- | --- |
| ID | SPEC-006 |
| Status | Accepted |
| Phase | A.2.7 |
| Component | Logging |
| Depends on | [SPEC-000](design-principles.md), [SPEC-001](sdk-client.md), [SPEC-002](configuration.md), [SPEC-005](transport.md) |
| Implementation | Not implemented |

## Status

Accepted — target architecture, not yet implemented. This specification has been
reviewed against the [Review Criteria](README.md#review-criteria) in
[Design Specifications](README.md) and is binding for implementation; see the
status model in [Design Specifications](README.md). A number of questions this
specification would normally answer are, deliberately, left open — see
[Open Questions](#open-questions).

## Purpose

`Logging` is the SDK's structured, file-based diagnostic logging. It turns
SDK-internal events — above all, the HTTP requests [Transport](transport.md)
executes — into structured, redacted log output, in Text or JSON.

`Logging` is architecturally different from [Configuration](configuration.md),
[Authentication](authentication.md), and [TLS](tls.md): those represent inert
information that some other component (`Transport`) later acts on. `Logger`, by
contrast, is itself one of the three shared infrastructure components
[SPEC-001](sdk-client.md) and [Component Model](../architecture/components.md)
already name (`Configuration`, `Logger`, `HTTP Transport`) — an active component
that consumes its own configuration and does real work. This specification defines
that work.

## Scope

**In scope:**

- Structured log events and their conceptual shape.
- Event IDs and how they differ from request IDs.
- SDK request IDs, server/correlation IDs, and request context.
- The `logrhythm_sdk` logger hierarchy.
- Ownership of logging infrastructure.
- The division of logging responsibility between `Transport` and API modules.
- Text and JSON output formats.
- File-based logging, destinations, and rotation.
- Log levels and DEBUG behavior.
- Endpoint/query logging and its mandatory redaction.
- How `Logging` reuses [SPEC-005](transport.md#redaction)'s central redaction
  component.
- How `Logging` interacts with exceptions, without either logging them itself.
- Failure behavior when logging itself fails.
- Performance constraints.
- Integration with `Configuration`.
- Validation and testability.

**Out of scope** (referenced only; defined by their own future specifications, or
explicitly deferred — see [Non-Goals](#non-goals) and
[Future Extensions](#future-extensions)):

- Concrete Python implementation.
- Concrete formatter classes.
- Concrete handler classes.
- Concrete event ID catalogs and numbering (see [Event IDs](#event-ids); the
  domain-based structure is decided, the catalog is not).
- Exact UUID string formatting below the length/field decisions in
  [Request IDs](#request-ids) (e.g. hyphenation, case).
- Logging to network destinations.
- SIEM forwarding.
- OpenTelemetry.
- The SDK's exception hierarchy.
- Concrete API endpoints.

## Responsibilities

`Logging`:

- represents SDK events as structured data, not primarily as free-form strings (see
  [Structured Events](#structured-events)).
- assigns a stable event ID to every defined SDK event (see
  [Event IDs](#event-ids)).
- generates and propagates a unique SDK request ID per outgoing request (see
  [Request IDs](#request-ids)).
- keeps a request's context available to every event produced during that request
  (see [Request Context](#request-context)).
- provides a consistent logger hierarchy under `logrhythm_sdk` (see
  [Logger Hierarchy](#logger-hierarchy)).
- is created or accepted, and owned accordingly, by `LogRhythmClient` as composition
  root (see [Ownership](#ownership)).
- produces Text and JSON output, primarily to files (see
  [Formats](#formats) and [Handlers and Destinations](#handlers-and-destinations)).
- redacts sensitive data using [SPEC-005](transport.md#redaction)'s central
  redaction component before any output (see [Redaction](#redaction)).
- avoids failing the SDK's actual operation because logging itself failed, within
  the bounds [Failure Behaviour](#failure-behaviour) describes.
- is testable without real network access or real secrets (see
  [Testability](#testability)).

## Non-Responsibilities

`Logging`:

- does not implement HTTP or transport logic itself — see
  [Transport Integration](#transport-integration).
- does not decide business logic or interpret API-specific data.
- does not implement its own secret detection — see [Redaction](#redaction).
- does not define the SDK's exception classes or hierarchy (see
  [Exception Interaction](#exception-interaction)).
- does not log to network destinations in version 1 (see [Non-Goals](#non-goals)).
- does not write to `stdout`/`stderr` uninvited (see
  [Handlers and Destinations](#handlers-and-destinations)).
- does not implement its own log rotation mechanism from scratch (see
  [File Rotation](#file-rotation)).

## Logging Model

**Decision: the SDK uses structured logging events.** Components should not
primarily produce free, unstructured log strings — this is a binding architectural
decision, not an open question. It follows from
[SPEC-000](design-principles.md#architecture-principles)'s "Explicit over implicit"
and "No hidden magic" principles: a structured event's fields are inspectable and
documentable, where a free-form string's meaning is not.

No concrete Python representation of an event is defined by this specification —
see [Structured Events](#structured-events) for the conceptual shape only.

## Structured Events

An event conceptually consists of, at minimum:

- an event ID (see [Event IDs](#event-ids))
- an event type
- a log level (see [Log Levels](#log-levels))
- a logger name (see [Logger Hierarchy](#logger-hierarchy))
- a message
- a timestamp
- structured fields
- an optional SDK request ID (see [Request IDs](#request-ids))
- an optional server/correlation ID (see [Request IDs](#request-ids))

This is a conceptual shape, not a class definition — no Python types, attributes, or
method signatures are specified here.

## Event IDs

Every defined SDK event has a stable event ID.

Event IDs:

- identify the **kind** of event — never a specific occurrence of it.
- are stable across minor releases.
- are intended to be human-readable and documentable.
- are **not** generated dynamically or randomly.
- are **not** used to identify a specific request — that is the SDK request ID's
  job (see [Request IDs](#request-ids)), not the event ID's. The two must not be
  conflated.

**Decision: event IDs are structured by technical domain, not by LogRhythm API.**
Example domains: `CLIENT`, `CONFIG`, `TRANSPORT`, `REQUEST`, `RESPONSE`,
`VALIDATION`, `ERROR`, `SECURITY`. Example event IDs:

- `LRSDK-TRANSPORT-0001`
- `LRSDK-REQUEST-0001`
- `LRSDK-ERROR-0001`

API-specific information (e.g. `admin`, `hosts`, `search`) is **not** part of the
event ID — it belongs in structured event fields instead (see
[Structured Events](#structured-events)). An event ID says what kind of technical
thing happened; the structured fields say what it happened to.

The concrete event catalog — the full list of defined event IDs and their exact
numbering within each domain — remains future work; it is not defined by this
specification. This is narrower than before: the domain-based structure above is
now decided, not open.

## Request IDs

**SDK request ID** (binding, not an open question):

- Every outgoing SDK request receives a unique SDK request ID.
- It is generated **locally by the SDK** — never derived from URL, host, query,
  credentials, or request body.
- It is generated **exactly once** per outgoing request, and reused for every log
  event produced during that request (see [Request Context](#request-context)).
- It is used independently of any server-assigned ID (see "Server request ID"
  below).
- It is bindingly based on whatever UUID standard is current at implementation
  time. This specification does not pin a specific UUID version now; it commits
  only to "the current UUID standard," not to a specific one.
- **Decision: internally, the full UUID is always used.** It remains available
  internally at all times, regardless of how it is displayed.
- **Decision: JSON logs use the full UUID.**
- **Decision: Text logs use, by default, the first 8 hexadecimal characters of the
  UUID.**

**Server request ID** (binding, not an open question):

- If LogRhythm returns its own request, trace, or correlation ID, it is tracked
  **separately** from the SDK request ID.
- At minimum: `request_id` denotes the SDK-generated UUID; `server_request_id` (or
  an equivalent field) denotes the server's ID.
- The two IDs must never be merged or substituted for one another.

## Request Context

All events produced during a single request must have access to the same request
context.

The request context conceptually contains, at minimum:

- the SDK request ID
- an optional server request ID
- the API area
- the resource / business area
- the sanitized endpoint (see
  [Endpoint and Query Logging](#endpoint-and-query-logging))
- a start time

**Decision: version 1 uses an explicit `RequestContext`.** Propagating request
context via `contextvars` (or another implicit mechanism) is **not** part of
version 1 — it remains a possible [Future Extension](#future-extensions), not an
open question. `RequestContext` here names a conceptual carrier of the fields
above, not a committed Python class definition.

## Logger Hierarchy

**Decision: the SDK uses the central logger namespace `logrhythm_sdk`.** Child
loggers are used beneath it, following the SDK's functional and technical
structure. Illustrative examples (not a committed final list — the exact number and
naming of child loggers follows later from the real module structure):

- `logrhythm_sdk.core.transport`
- `logrhythm_sdk.core.config`
- `logrhythm_sdk.admin`
- `logrhythm_sdk.admin.hosts`
- `logrhythm_sdk.admin.entities`
- `logrhythm_sdk.aie.rules`
- `logrhythm_sdk.metrics`
- `logrhythm_sdk.alarms`
- `logrhythm_sdk.search`

**Binding rules:**

- Child loggers receive no handlers of their own.
- Child loggers propagate to the centrally configured SDK logger.
- API modules configure no handlers.
- API modules configure no global loggers.
- No duplicate handler configuration.
- No uncontrolled access to the host application's root logger.

## Ownership

`LogRhythmClient` is the composition root for logging — this is not a new rule, but
[SPEC-001](sdk-client.md#ownership)'s existing ownership rule for `Logger` (one of
the three shared infrastructure components), elaborated for logging specifically:

- `LogRhythmClient` creates or accepts the logging infrastructure (see
  [SPEC-001](sdk-client.md#dependency-injection)).
- It holds the central SDK logger.
- It provides matching child loggers to `core` and API components (see
  [Logger Hierarchy](#logger-hierarchy)).
- It manages the lifecycle only of handlers and resources it created itself,
  consistent with [SPEC-001](sdk-client.md#ownership)'s general rule.

**Externally injected loggers** (binding, not an open question):

- remain owned by the caller who supplied them.
- are never reconfigured by the SDK.
- are never closed by the SDK.
- never receive additional handlers without being asked.

## Transport Integration

HTTP- and request-related logs should originate centrally in
[`HttpTransport`](transport.md#transport-model) as much as possible — this
specification is where the decision [SPEC-005](transport.md#logging-metadata)
explicitly deferred ("`Transport` does not decide what is actually logged... that
decision belongs exclusively to a future logging specification (SPEC-006)") is
made.

`Transport` logs, in particular:

- request creation
- request start
- request end
- transport errors
- response receipt
- status code
- duration
- the sanitized endpoint, including sanitized query string
- TLS mode
- timeout metadata
- response size
- the server request ID
- future retry metadata

This draws directly on the "Logging Metadata" and "Debug Metadata"
[SPEC-005](transport.md#logging-metadata) already makes available — `Logging`
decides which of it is actually emitted, and how.

## API Module Logging

API resources and API clients log only domain-level information `Transport` cannot
know. Examples:

- model validation failed
- a documented API special case was detected
- pagination state changed
- a search job's state changed
- a business-level operation completed

**API modules must not duplicate** what `Transport` already logs:

- request start
- HTTP status
- duration
- endpoint
- transport errors
- response receipt

## Formats

Version 1 supports exactly two formats: **Text** and **JSON**.

**Decision: when SDK-owned logging is enabled, the default format is Text**, unless
overridden.

**Text:**

- primarily human-readable.
- consistently represents key fields, including: timestamp, log level, logger name,
  event ID, request ID (if present), message, and central metadata.

**JSON:**

- machine-readable and structured.
- contains structured fields **without** first collapsing them into free text.
- exact field ordering and which JSON library is used internally are not defined by
  this specification.

## Handlers and Destinations

**Decision: the SDK's own logging is disabled by default.** No file (or other)
handler is created unless the caller explicitly enables SDK-owned logging.

**Decision: version 1 uses file-based logging primarily**, once enabled. Bindingly
provided:

- a configurable file path
- a configurable format (see [Formats](#formats))
- a configurable log level (see [Log Levels](#log-levels))

**A file path is required as soon as the SDK is to create its own file handler.**
There is no built-in default file path — see
[Failure Behaviour](#failure-behaviour) for what happens when SDK-owned logging is
enabled without a usable path.

**Decision: version 1 includes console logging as an explicit, off-by-default
option.** When SDK-owned logging is enabled, console logging is **disabled** unless
separately turned on. The SDK must never write to `stdout` or `stderr` uninvited.

See [Log Levels](#log-levels), [Formats](#formats), and
[File Rotation](#file-rotation) for the concrete defaults that apply once
SDK-owned logging is enabled.

## File Rotation

File rotation is supported. Its implementation should build on established
mechanisms already present in Python's logging infrastructure, or comparable
standard mechanisms — **not** a bespoke rotation implementation built from scratch
(see [Non-Goals](#non-goals)).

Version 1 supports, at minimum, **size-based** rotation. Conceptually
configurable:

- maximum file size
- number of retained files

**Decision: when SDK-owned logging is enabled, the default rotation is 10 MiB per
file, with 5 backups retained**, unless overridden.

Time-based rotation is a possible [Future Extension](#future-extensions), not part
of version 1.

## Log Levels

Version 1 supports, at minimum:

- `DEBUG`
- `INFO`
- `WARNING`
- `ERROR`
- `CRITICAL`

**No separate `TRACE` level in version 1** (see [Non-Goals](#non-goals); `TRACE` is
a possible [Future Extension](#future-extensions)).

**Decision: when SDK-owned logging is enabled, the default level is `INFO`**,
unless overridden.

General semantics:

- **`DEBUG`** — detailed diagnostic information.
- **`INFO`** — regular SDK lifecycle and request events.
- **`WARNING`** — unsafe or unusual, but continuable, states.
- **`ERROR`** — failed operations.
- **`CRITICAL`** — severe, SDK-wide states, used only where genuinely warranted.

Concrete per-event levels are determined later, in a future event catalog — not
decided here.

## Debug Logging

`DEBUG` extends structured events with additional diagnostic fields. Possible
fields:

- the full sanitized endpoint
- sanitized headers
- sanitized query string
- sanitized request body
- sanitized response body
- TLS mode
- timeout configuration
- URL resolution
- response decoding metadata

**Even in `DEBUG`** (binding, not an open question):

- no secrets.
- no unsanitized headers.
- no unsanitized query parameters.
- no unsanitized bodies.
- no credentials.

**`DEBUG` must never mean that redaction is disabled.** This is one of the most
important constraints in this specification and admits no exception.

**Decision: `DEBUG` alone does not enable request or response bodies.** Bodies are
logged only when an additional, explicit configuration option is also active (e.g.
an `include_bodies` option) — `DEBUG` by itself is not sufficient. Bindingly, in
addition:

- **Maximum default body size: 16 KiB per body.**
- **Content beyond that size is marked as truncated**, not silently cut off without
  indication.
- **Binary content is never logged unfiltered.**
- **Redaction remains active at all times** for bodies, exactly as for every other
  category in [Redaction](#redaction) — this is not a separate rule, only a
  restatement that it applies here too.

## Endpoint and Query Logging

The sanitized endpoint, including sanitized query string, may be logged. Example:

```text
/admin/hosts?page=2&limit=100
```

Sensitive query parameters must be redacted before output. The redaction rules from
[SPEC-005](transport.md#redaction) apply bindingly and are not redefined here.

Full URLs may only be used after sanitization. The target URL, host, and query must
never appear unfiltered in exceptions or warnings.

## Redaction

`Logging` uses **exclusively** the central redaction component from
[SPEC-005](transport.md#redaction). It implements **no parallel or independent
secret detection of its own.**

Redaction happens before:

- formatting
- handler output
- exception context, if reused (see [Exception Interaction](#exception-interaction))
- debug output (see [Debug Logging](#debug-logging))

Redaction covers, at minimum:

- headers
- query parameters
- request bodies
- response bodies
- structured event fields

**A redaction failure must never result in unredacted output.** When in doubt, the
affected value must be fully discarded or replaced — never passed through
unredacted. This is a fail-closed requirement, consistent with
[SPEC-000](design-principles.md#security-principles)'s "Security by default"
principle.

## Exception Interaction

Exceptions do not log themselves. An exception is either:

- logged and then re-raised/propagated, or
- only propagated, without being logged at that layer,

depending on which calling layer is responsible for it. An exception must **not**
be automatically logged identically at multiple layers — the logging design must
avoid duplicate error entries.

The concrete exception hierarchy follows in a future specification (`SPEC-007`),
consistent with this series' numbering scheme
([Design Specifications](README.md#numbering)) — it is not defined here, and this
specification does not anticipate its shape.

## Failure Behaviour

**Logging must not, in general, cause the SDK's actual operation to fail.** This is
a deliberate, explicit exception to
[SPEC-000](design-principles.md#implementation-principles)'s "Fail fast" principle,
stated and reasoned here rather than silently diverging from it, per
[Design Specifications](README.md#review-criteria)' review criteria: a logging
failure is not the same category of problem as invalid input or missing
configuration, and letting it abort an otherwise-successful SDK operation would
itself be a surprising, disproportionate failure mode.

If logging itself fails:

- no secrets may be output as a result.
- the actual SDK operation should continue where possible.
- no recursive logging failures may occur.
- no infinite loop may result.

**The one exception to "logging must not fail the operation"** applies only to
errors that must mandatorily be validated when the client is built. For that narrow
category, failing at construction time is consistent with, not an exception to,
Fail Fast.

**Decision: if SDK-owned logging is enabled and any of the following holds**:

- no file path is present,
- a structurally valid path is unusable,
- the path is not writable, or
- the file handler cannot be initialized,

**client/configuration initialization must fail**, per Fail Fast — this is binding,
not an open question. Runtime failures that occur while writing to an already
correctly initialized log are, as stated above, non-fatal: they do not cause the
SDK's actual operation to fail.

The exception boundary is [SPEC-007](exceptions.md#configuration-errors)'s existing
`LoggingConfigurationError`. Absence of `file` while SDK-owned logging is enabled is
known without filesystem access and is raised at Configuration construction. A
structurally valid file path is checked for filesystem usability, writability, and
handler initialization only when logging infrastructure is built. Both boundaries
use `LoggingConfigurationError`; neither case is reclassified as ordinary
`ConfigurationValidationError`.

## Performance

`Logging` should:

- open no network connections.
- call no external services.
- not unnecessarily block the request path.
- not copy full bodies where avoidable.
- prepare `DEBUG` data only when the `DEBUG` level is actually active.

Asynchronous logging is not part of version 1 (see
[Future Extensions](#future-extensions)).

## Configuration Integration

[SPEC-002](configuration.md#configuration-schema) defines this concretely: its
Configuration Model names "Logging-related inputs" as one of the groups a resolved
`Configuration` holds (file path, format, level, rotation parameters, conceptually).

Unlike [Authentication](authentication.md#integration-with-configuration) or
[TLS](tls.md#configuration-integration) — which remain purely inert data until
`Transport` acts on them — logging-related `Configuration` values are consumed and
acted upon by `Logging` itself, since `Logger` is a real, active shared
infrastructure component (see [Purpose](#purpose)). The relationship is closer to
how `Configuration`'s connection information feeds `Transport` (an active
component that uses it) than to how authentication or TLS inputs are merely
represented and passed along.

Because a resolved `Configuration` is immutable
([SPEC-002](configuration.md#immutability-and-lifecycle)), logging settings cannot
change after resolution without resolving a new `Configuration`. Their concrete
configuration fields are defined by
[SPEC-002](configuration.md#logging-configuration); this specification remains the
source of truth for logging semantics and defaults.

## Validation

Consistent with [SPEC-002](configuration.md#validation)'s categories:

- **At `Configuration` resolution** (syntactic/structural/semantic-local only): for
  example, that the log level is one of the known values (see
  [Log Levels](#log-levels)), and that the format is one of `Text`/`JSON` (see
  [Formats](#formats)). Unknown keys, invalid types or enums, invalid numeric bounds,
  and a syntactically invalid file-path value are ordinary
  `ConfigurationValidationError` cases.
- **At Configuration construction, but outside ordinary schema validation:** if
  SDK-owned logging is enabled and `file` is absent, construction fails as
  `LoggingConfigurationError` without touching the filesystem.
- **Not** validated at `Configuration` resolution: whether the log file path is
  actually usable. Confirming that requires real I/O, which
  [SPEC-002](configuration.md#validation) deliberately excludes from
  `Configuration`-level validation ("no reachability checks").
- Usability of the log file path is instead checked when the logging
  infrastructure is actually built, as part of `LogRhythmClient`/`Configuration`
  initialization (see [Ownership](#ownership) and
  [Failure Behaviour](#failure-behaviour)): if SDK-owned logging is enabled and the
  structurally valid path is unusable or unwritable, or the handler cannot be
  initialized, initialization fails as `LoggingConfigurationError` per Fail Fast —
  this is now decided, not an open question.
- No network validation, and no validation of a remote destination — version 1 has
  none (see [Non-Goals](#non-goals)).

## Testability

- `Logging` must be fully testable without real network access, consistent with
  [SPEC-000](design-principles.md#testability) ("Mockable infrastructure").
- Loggers are injectable, mirroring
  [SPEC-001](sdk-client.md#dependency-injection)'s existing rule for `Logger` — tests
  can substitute a fake or mock logger.
- Redaction (see [Redaction](#redaction)) must be independently testable, consistent
  with [SPEC-005](transport.md#testability)'s equivalent requirement.
- No real secrets, credentials, hosts, or file paths tied to production systems are
  used in this specification or in any test; placeholders only.
- Validation and formatting behavior must be deterministic: the same inputs always
  produce the same result.

## Examples

Pseudocode only — illustrative of intended usage, not a class signature or real
implementation. Placeholder values only; no real secrets or production file paths.

**Explicitly enabled file-based logging:**

```python
configuration = Configuration(
    logrhythm=placeholder_logrhythm_settings,
    logging={"enabled": True, "file": "sdk.log"},
)
client = LogRhythmClient(configuration)
# The path has already been resolved by Configuration. LogRhythmClient later creates
# and owns the logging infrastructure. Without enabled=True, SDK logging is disabled.
```

**Dependency injection for tests (a fake logger, no real file involved):**

```python
client = LogRhythmClient(
    configuration=test_configuration,
    logger=fake_logger,  # implements the SDK's logger contract; owned by the caller
    transport=fake_transport,
)
```

**Conceptual shape of a structured event (illustrative only, not a class):**

```text
event_id:      <stable event identifier>
event_type:    <kind of event>
level:         INFO
logger:        logrhythm_sdk.core.transport
message:       "request completed"
timestamp:     <timestamp>
request_id:    <SDK-generated UUID>
server_request_id: <server-supplied ID, if any>
fields:        { method: "GET", endpoint: "/admin/hosts", status: 200, duration_ms: 42 }
```

## Open Questions

These are explicitly undecided. They must not be resolved silently by
implementation; each requires an explicit decision (and, where architecturally
significant, an ADR) before it can move out of this list.

- **Event catalog and numbering.** The full catalog of defined event IDs and their
  exact numbering within each domain (see [Event IDs](#event-ids)) — the
  domain-based structure itself is decided; the catalog is not.

## Future Extensions

These are possible ideas for later, explicitly non-binding, and do not represent any
architectural decision or part of SPEC-006:

- OpenTelemetry.
- Syslog.
- Windows Event Log.
- Journald.
- Network logging.
- SIEM forwarding.
- Asynchronous logging.
- Time-based rotation.
- External event catalogs.
- Configurable event filters.
- `TRACE` level.
- `contextvars`-based request context propagation (see
  [Request Context](#request-context)).

## Non-Goals

This specification, and by extension `Logging` itself, explicitly does not cover:

- Network logging in version 1.
- SIEM forwarding.
- A custom logging library.
- A custom rotation implementation.
- Secrets appearing in logs, under any circumstance.
- Unstructured free-form logs as the primary model.
- Self-logging exceptions.
- Handler configuration inside API modules.
- Global root-logger configuration.
- A `TRACE` level in version 1.

## References

- [SPEC-000 — Design Principles](design-principles.md)
- [SPEC-001 — SDK Client](sdk-client.md)
- [SPEC-002 — Configuration](configuration.md)
- [SPEC-005 — Transport](transport.md)
- [Architecture Overview](../architecture/overview.md)
- [Component Model](../architecture/components.md)
- No existing ADR (see [docs/adr/](../adr/README.md)) is specific to logging
  architecture; none is referenced here as directly applicable.
