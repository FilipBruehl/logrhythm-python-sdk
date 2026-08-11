# SPEC-007 — Exception Handling

| Field | Value |
| --- | --- |
| ID | SPEC-007 |
| Status | Accepted |
| Phase | A.2.8 |
| Component | Exceptions |
| Depends on | [SPEC-000](design-principles.md), [SPEC-001](sdk-client.md), [SPEC-002](configuration.md), [SPEC-005](transport.md), [SPEC-006](logging.md) |
| Implementation | Not implemented |

## Status

Accepted — target architecture, not yet implemented. This specification has been
reviewed against the [Review Criteria](README.md#review-criteria) in
[Design Specifications](README.md) and is binding for implementation; see the
status model in [Design Specifications](README.md). A small number of questions
this specification would normally answer are, deliberately, left open — see
[Open Questions](#open-questions).

## Purpose

`Exceptions` is the SDK's public exception architecture. It is what several earlier
specifications in this series explicitly deferred to: [SPEC-001](sdk-client.md#public-api)
("the specific exception type raised is defined by a future specification"),
[SPEC-002](configuration.md#error-behaviour), [SPEC-005](transport.md#error-behaviour),
and [SPEC-006](logging.md#exception-interaction) ("the concrete exception hierarchy
follows in a future specification (`SPEC-007`)") all described error *categories*
without naming classes. `Exceptions` is where those categories become a concrete,
stable public hierarchy.

Its purpose is narrow: give every failure the SDK can encounter a predictable,
documented shape — without ever exposing the internals of whatever library or
mechanism actually caused it.

## Scope

**In scope:**

- The public exception hierarchy and its single root.
- The main exception categories and their minimum subclasses.
- The conceptual mapping from HTTP status codes to `ApiError` subclasses.
- Structured exception context and response snippets.
- Exception chaining, and where the SDK does — and does not — translate an
  underlying error.
- How exceptions interact with logging, without logging themselves.
- How redaction applies to exception context, consistently with
  [SPEC-005](transport.md#redaction) and [SPEC-006](logging.md#redaction).
- What is publicly exported, and from where.
- Testability requirements.

**Out of scope** (referenced only; defined by their own future specifications, or
explicitly deferred — see [Non-Goals](#non-goals) and
[Future Extensions](#future-extensions)):

- Concrete Python implementation.
- Concrete exception classes (as code).
- Retry implementation.
- Concrete API endpoints.
- Logging implementation.
- Transport implementation.

## Responsibilities

`Exceptions`:

- defines a single public root, `LogRhythmSdkError`, that every public SDK
  exception inherits from (see [Exception Hierarchy](#exception-hierarchy)).
- defines the main exception categories and their minimum subclasses (see
  [Configuration Errors](#configuration-errors) through
  [API Errors](#api-errors)).
- fully encapsulates third-party library errors — no public SDK exception exposes
  a third-party base class (see [Exception Hierarchy](#exception-hierarchy)).
- carries structured, machine-usable diagnostic context (see
  [Exception Context](#exception-context)).
- chains known, secret-free technical causes using `raise ... from ...`, preserving
  `__cause__` (see [Exception Chaining](#exception-chaining)).
- redacts sensitive data from all exception context, consistently with
  [SPEC-005](transport.md#redaction) and [SPEC-006](logging.md#redaction) (see
  [Redaction](#redaction)).
- is publicly exported from a dedicated location, deliberately not the package
  root in full (see [Public API](#public-api)).
- is testable without real network access or real secrets (see
  [Testability](#testability)).

## Non-Responsibilities

`Exceptions`:

- does not log itself — see [Logging Interaction](#logging-interaction).
- does not implement retry logic (see [Non-Goals](#non-goals)).
- does not implement HTTP, transport, or logging behavior itself.
- does not mask unknown programming errors as SDK errors (see
  [Exception Chaining](#exception-chaining)).
- does not perform business logic or interpret API-specific data beyond
  structuring what other components already determined.

## Exception Hierarchy

**Decision: every public SDK exception inherits, directly or indirectly, from a
single root: `LogRhythmSdkError`.** No public exception inherits from httpx, or any
other third-party exception type — this is a direct application of
[SPEC-000](design-principles.md#architecture-principles)'s "Stable abstractions"
principle, the same principle [SPEC-005](transport.md#transport-model) already
applied to `TransportProtocol`: consumers depend on the SDK's own contract, never
on a third-party library's types.

**Decision: the main categories are, at minimum:**

- `ConfigurationError` (see [Configuration Errors](#configuration-errors))
- `ClientStateError` (see [Client State Errors](#client-state-errors))
- `TransportError` (see [Transport Errors](#transport-errors))
- `SerializationError` (see [Serialization Errors](#serialization-errors))
- `ModelError` (see [Model Errors](#model-errors))
- `ApiError` (see [API Errors](#api-errors))

Subclasses exist **only** for domain specialization — never for their own sake.
**The hierarchy is kept flat**: deep inheritance chains are not part of this
architecture, consistent with
[SPEC-000](design-principles.md#architecture-principles)'s "Composition over
inheritance" principle. No Python class definitions, method signatures, or
attributes are given here — consistent with every other specification in this
series.

## Configuration Errors

`ConfigurationError` covers failures in resolving or validating `Configuration`
(see [SPEC-002](configuration.md#error-behaviour)). Minimum subclasses:

- `ConfigurationSourceError` — a configuration source itself could not be used (for
  example, a file `from_config(...)` was pointed at could not be read; see
  [SPEC-002, Configuration Sources](configuration.md#configuration-sources)).
- `ConfigurationFormatError` — a configuration source was readable but not
  parseable in its expected format (see
  [SPEC-002, Configuration Sources](configuration.md#configuration-sources)).
- `ConfigurationValidationError` — a resolved value failed validation (see
  [SPEC-002, Error Behaviour](configuration.md#error-behaviour): missing required
  values, invalid values, conflicting values, unknown fields, invalid
  combinations). For credential-bearing `Configuration`, both direct programmatic
  construction and file loading expose this sanitized SDK exception rather than an
  input-bearing Pydantic validation exception; see
  [SPEC-002, Pydantic Validation Boundary](configuration.md#pydantic-validation-boundary).
- `LoggingConfigurationError` — the specific case
  [SPEC-006](logging.md#failure-behaviour) already establishes: SDK-owned logging
  is enabled but its file path is missing, a structurally valid path is unusable or
  unwritable, or its handler cannot be initialized. This subclass exists because
  [SPEC-006](logging.md#failure-behaviour) singles this case out as a mandatory
  Fail Fast failure at client/configuration initialization, distinct from ordinary
  configuration validation. Missing `file` is detected at Configuration
  construction; filesystem usability, writability, and handler initialization are
  checked only when logging infrastructure is built. Structurally invalid logging
  field values remain `ConfigurationValidationError` cases.

## Client State Errors

`ClientStateError` covers invalid use of `LogRhythmClient` itself, independent of
any particular request. Minimum subclasses:

- `ClientInitializationError` — `LogRhythmClient` could not be constructed.
- `ClientClosedError` — the client was used after being closed (see
  [SPEC-001, Lifecycle](sdk-client.md#lifecycle); whether a closed client can be
  reused at all remains an open question there — this exception applies to
  whichever "used while closed" cases that resolution ultimately disallows).

This list is a minimum, not an exhaustive, set: [SPEC-010](api-modules.md#api-configuration)
documents a further `ClientStateError` subclass, `ApiNotConfiguredError`, for using
an API area that is not configured or is explicitly disabled — it is not repeated
in full here.

## Transport Errors

`TransportError` covers failures [SPEC-005](transport.md#error-behaviour) already
categorizes conceptually. Minimum subclasses:

- `TransportConnectionError` — a connection could not be established (e.g. DNS
  resolution failure, connection refused).
- `TransportTimeoutError` — any of [SPEC-005](transport.md#timeout-handling)'s
  timeout categories (connect, read, write, pool) elapsed. **Decision: this uses a
  single class with a structured `timeout_kind` field** — there are no separate
  public subclasses per timeout category.
- `TransportTlsError` — a TLS handshake failed, kept distinct from
  `TransportConnectionError` because it is a TLS-specific failure (see
  [SPEC-005, TLS Integration](transport.md#tls-integration)).
- `TransportProtocolError` — the underlying HTTP exchange itself was malformed at
  the protocol level (distinct from a well-formed response with an unexpected
  status or an unparseable JSON body, which are `ApiError` and
  `SerializationError` concerns respectively).
- `TransportRequestError` — the request could not be constructed or sent, distinct
  from a failure that occurred once a connection existed.

`3xx` responses (unexpected because [SPEC-005](transport.md#response-handling)
does not follow redirects) and `4xx`/`5xx` responses are **not** `TransportError` —
they are `ApiError`, because a response was actually received (see
[API Errors](#api-errors) and [HTTP Mapping](#http-mapping)).

## Serialization Errors

`SerializationError` covers failures converting to or from the wire format.
Minimum subclasses:

- `RequestSerializationError` — an outgoing request body could not be serialized.
- `ResponseDecodingError` — a response body could not be decoded as expected (see
  [SPEC-005, JSON handling](transport.md#response-handling): invalid/malformed
  JSON where JSON was expected).

## Model Errors

`ModelError` covers failures converting between raw data and typed models.
Minimum subclasses:

- `RequestValidationError` — data the caller supplied fails local validation
  before being sent.
- `ResponseValidationError` — data LogRhythm returned fails validation against the
  expected model.

**Decision: local request validation and server-response validation are strictly
separate** — a `RequestValidationError` is never raised for a problem in data that
came back from the server, and vice versa. This distinction matters because the two
have different causes and different remedies for a caller.

## API Errors

`ApiError` represents **exclusively** errors where an HTTP response was actually
received — never a connection-level or transport-level failure (those are
`TransportError`). Minimum subclasses:

- `UnexpectedRedirectError` — a `3xx` response (see
  [SPEC-005, Response Handling](transport.md#response-handling)).
- `ClientResponseError` — a `4xx` response without a more specific subclass below.
  - `AuthenticationError`
  - `AuthorizationError`
  - `ResourceNotFoundError`
  - `ConflictError`
  - `RateLimitError`
  - `ApiValidationError`
- `ServerResponseError` — a `5xx` response.

**Decision: not every HTTP status gets its own exception.** Only status codes with
clear, distinct business meaning are specialized (see
[HTTP Mapping](#http-mapping)); everything else falls back to `ClientResponseError`
or `ServerResponseError`.

## Universal LogRhythm Error

LogRhythm returns a standardized error body on (at least some) error responses.

**Decision: this is modeled as a separate, structured error object** — not folded
directly into `ApiError`'s own attributes. `ApiError` holds this object
**optionally**, since not every error response is guaranteed to include one (or
LogRhythm's standard error body may not be documented for every case).

**Decision: the HTTP status code and LogRhythm's own status code inside that error
body are tracked separately** — see `http_status_code` and `vendor_status_code` in
[Exception Context](#exception-context). They are not assumed to always agree, and
are never merged into a single field.

**Decision: a missing or invalid error body never prevents `ApiError` creation.**
`Exceptions` does not require LogRhythm's standard error body to be present or
well-formed in order to raise an appropriate `ApiError` — the HTTP status code
alone is always sufficient. The exact structure of LogRhythm's standard error body,
where not fully documented by the vendor, is an [Open Question](#open-questions).

## HTTP Mapping

The conceptual mapping from HTTP status to `ApiError` subclass (see
[API Errors](#api-errors)):

| Status | Exception |
| --- | --- |
| `401` | `AuthenticationError` |
| `403` | `AuthorizationError` |
| `404` | `ResourceNotFoundError` |
| `409` | `ConflictError` |
| `422` | `ApiValidationError` |
| `429` | `RateLimitError` |
| other `4xx` | `ClientResponseError` |
| `5xx` | `ServerResponseError` |
| `3xx` | `UnexpectedRedirectError` |

This mapping is binding for the statuses listed. It does not imply that every
conceivable status code has been enumerated — unlisted codes fall back to the
appropriate general category (`ClientResponseError` or `ServerResponseError`) per
[API Errors](#api-errors).

## Exception Context

Exceptions may carry structured diagnostic information. Possible fields include:

- `request_id` (see [SPEC-006, Request IDs](logging.md#request-ids))
- `server_request_id` (see [SPEC-006, Request IDs](logging.md#request-ids))
- `event_id` (see [SPEC-006, Event IDs](logging.md#event-ids))
- `api_area`
- `resource`
- `operation`
- `method`
- `sanitized_endpoint`
- `http_status_code`
- `vendor_status_code` (see
  [Universal LogRhythm Error](#universal-logrhythm-error))
- `retry_after`
- `safe_response_snippet` (see [Response Snippets](#response-snippets))

**Not every exception needs every field** — which fields apply depends on the
exception's category (for example, `http_status_code` only makes sense for
`ApiError`).

**Decision: public exception objects are immutable after creation.** Diagnostic
information is set only when the exception is constructed. Mutating exception
attributes afterward is not part of this architecture.

**Decision: exception messages are for humans only.** Code must never parse an
exception's message text to make decisions — machine-relevant information is
available exclusively through the structured attributes above. This follows
[SPEC-000](design-principles.md#api-design)'s "No surprises" principle: a caller
should never need to resort to string matching against prose.

## Response Snippets

An `ApiError` may carry a sanitized excerpt of the response body. Bindingly:

- **Maximum 4 KiB.**
- **Redaction is mandatory** — the same central redaction
  [SPEC-005](transport.md#redaction) and [SPEC-006](logging.md#redaction) already
  use, not a separate mechanism (see [Redaction](#redaction)).
- **Binary content is never included unfiltered.**
- **Truncation is marked**, not silently applied without indication — consistent
  with [SPEC-006](logging.md#debug-logging)'s identical rule for `DEBUG` bodies.

## Exception Chaining

**Decision: known technical causes are normally chained using
`raise ... from ...`.** The original cause remains available via `__cause__` when
it and all transitively reachable data are known to be secret-free.

**Security-sensitive exception translation is the binding exception to that
preference.** A lower-level exception that contains or may retain credentials,
configuration input, request/response content, or other secrets is not exposed as
`__cause__` or `__context__`. Translation must discard that raw exception and raise
the sanitized SDK exception outside its active handling context, or use an
equivalent mechanism that makes no input-bearing exception publicly reachable.
This applies in particular to Configuration's Pydantic and parser errors; rendered
masking alone is insufficient because structured error APIs can retain raw input.
The exposed exception may have no cause/context or only a separately sanitized,
secret-free one.

**Decision: only known infrastructure errors are translated.** `Exceptions`
translates specific, expected underlying error types (e.g. a specific httpx
connection error becoming a `TransportConnectionError`) into the corresponding
`LogRhythmSdkError` subclass. It does **not** translate errors it does not
specifically recognize.

**Decision: there is no catch-all translation.** A blanket `except Exception` that
turns everything into `LogRhythmSdkError` is explicitly **not** part of this
architecture. Unknown programming errors (bugs) must **not** be masked as SDK
errors — they propagate as themselves. Only known system/library boundaries are
translated; everything else is left visible, consistent with
[SPEC-000](design-principles.md#api-design)'s "No surprises" principle. Disguising
an unrelated bug as a domain-level `LogRhythmSdkError` would itself be a surprising
failure mode.

## Logging Interaction

Exceptions do not log themselves — this restates, from the exception side,
exactly what [SPEC-006](logging.md#exception-interaction) already establishes from
the logging side: an exception is either logged and then re-raised/propagated, or
only propagated, depending on which calling layer is responsible for it, and must
never be logged identically at multiple layers. `Exceptions` introduces no
exception to that rule.

## Redaction

**Decision: exception context follows exactly the same redaction rules as
[Transport](transport.md#redaction) and [Logging](logging.md#redaction) — not a
separate or parallel mechanism.**

Secrets must never appear in:

- `str()` output
- `repr()` output
- exception messages
- context fields (see [Exception Context](#exception-context))
- response snippets (see [Response Snippets](#response-snippets))
- `__cause__`, `__context__`, structured lower-level error data, or any transitively
  reachable exception object

This is not a new rule — it is [SPEC-005](transport.md#redaction)'s and
[SPEC-006](logging.md#redaction)'s existing requirement, applied to exceptions as
the third consumer of the same central redaction component.

## Public API

**Decision: all public exceptions are provided via `logrhythm_sdk.exceptions`.**

**Decision: the package root exports at most `LogRhythmSdkError`** — not every
subclass. This is consistent with
[SPEC-000](design-principles.md#documentation-principles)'s emphasis on a
deliberate, minimal public surface (see also
[SPEC-001](sdk-client.md#public-api), which took the same approach for
`LogRhythmClient` itself): a caller who needs a specific subclass imports it from
`logrhythm_sdk.exceptions` explicitly, rather than finding the entire exception
tree implicitly available from the package root.

## Failure Behaviour

**Decision: constructing or raising an exception must never itself raise a
different, unrelated exception.** If building structured context (e.g. applying
redaction — see [Redaction](#redaction)) cannot proceed safely, the affected field
is discarded or replaced, exactly as [SPEC-006](logging.md#redaction) already
requires for redaction failures generally — it does not abort exception creation
or produce a second, masking failure.

This specification does not introduce new Fail Fast obligations beyond what
[SPEC-000](design-principles.md#implementation-principles) and the specifications
this one depends on already establish; `Exceptions` is itself how those
obligations are surfaced to a caller.

## Validation

`Exceptions` does not independently validate business data — that already happened
in the component that raises a given exception (`Configuration`, `Transport`,
model conversion, etc.; see [SPEC-002](configuration.md#validation) and
[SPEC-005](transport.md#validation)). What `Exceptions` is responsible for is
narrower: ensuring a raised exception's structured context (see
[Exception Context](#exception-context)) is consistent with its category — for
example, that an `ApiError` carries an `http_status_code`, not that the status
code itself is "valid" in some independent sense.

## Testability

- `Exceptions` must be fully testable without real network access, consistent with
  [SPEC-000](design-principles.md#testability).
- Tests can construct any public exception directly, with placeholder context.
- Exception chaining (see [Exception Chaining](#exception-chaining)) must be
  testable — a test can assert that `__cause__` is set as expected for a known,
  secret-free translated error and is not exposed for an input-bearing error.
- Redaction of exception context (see [Redaction](#redaction)) must be
  independently testable, consistent with
  [SPEC-005](transport.md#testability) and [SPEC-006](logging.md#testability).
- No real secrets, credentials, hosts, or response bodies tied to production
  systems are used in this specification or in any test; placeholders only.

## Examples

Pseudocode only — illustrative of intended usage, not a committed API surface, not
a real implementation, and not a claim about any concrete field name or class
signature. Placeholder values only; no real secrets or response data.

**Importing from the dedicated exceptions module (not the package root):**

```python
from logrhythm_sdk.exceptions import ResourceNotFoundError

try:
    client.search.some_operation(...)
except ResourceNotFoundError as error:
    # structured attributes are available for programs; the message is for humans
    print(error.http_status_code, error.sanitized_endpoint, error.request_id)
```

**Conceptual chaining of a known infrastructure error (illustrative only):**

```python
try:
    ...  # some underlying, known connection failure occurs
except SomeKnownUnderlyingConnectionError as underlying:
    raise TransportConnectionError(...) from underlying
    # __cause__ is preserved; unrecognized errors are never caught this broadly
```

**Conceptual shape of `ApiError` context (illustrative only, not a class):**

```text
exception:          AuthenticationError
request_id:          <SDK-generated UUID>
server_request_id:   <server-supplied ID, if any>
http_status_code:    401
vendor_status_code:  <LogRhythm's own status code, if present>
sanitized_endpoint:  /admin/hosts
safe_response_snippet: <redacted, truncated excerpt, if available>
```

## Open Questions

These are explicitly undecided. They must not be resolved silently by
implementation; each requires an explicit decision (and, where architecturally
significant, an ADR) before it can move out of this list.

- **Exact structure of LogRhythm's standard error body.** Where LogRhythm's own
  documentation does not fully specify it (see
  [Universal LogRhythm Error](#universal-logrhythm-error)).
- **Concrete event catalog for exceptions.** Which event IDs (see
  [SPEC-006, Event IDs](logging.md#event-ids)) correspond to which exceptions —
  deferred the same way the general event catalog is deferred in
  [SPEC-006](logging.md#open-questions).
- **Future retry classification.** How exceptions would be classified as
  retryable or not, if/when retry support is added (see
  [Future Extensions](#future-extensions)).
- **Additional API-specific exception subclasses.** Whether individual API modules
  will need their own specialized `ApiError` subclasses beyond the minimum set in
  [API Errors](#api-errors), once real endpoints are implemented.

## Future Extensions

These are possible ideas for later, explicitly non-binding, and do not represent
any architectural decision or part of SPEC-007:

- Retry policies.
- Exception localization.
- Additional API-specific exceptions.
- Automatic problem reports.
- Exception telemetry.

## Non-Goals

This specification, and by extension `Exceptions` itself, explicitly does not
cover:

- Retry logic. Version 1 has none — see
  [SPEC-005, Non-Goals](transport.md#non-goals). Retry-related information (e.g.
  `retry_after`) may only be provided as optional metadata (see
  [Exception Context](#exception-context)), never acted on automatically.
- HTTP implementation.
- Transport implementation.
- Logging implementation.
- Concrete API endpoints.
- Concrete Python exception classes (as code).

## References

- [SPEC-000 — Design Principles](design-principles.md)
- [SPEC-001 — SDK Client](sdk-client.md)
- [SPEC-002 — Configuration](configuration.md)
- [SPEC-005 — Transport](transport.md)
- [SPEC-006 — Logging](logging.md)
- [Architecture Overview](../architecture/overview.md)
- [Component Model](../architecture/components.md)
- No existing ADR (see [docs/adr/](../adr/README.md)) is specific to exception
  architecture; none is referenced here as directly applicable.
