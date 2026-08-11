# SPEC-005 — Transport

| Field | Value |
| --- | --- |
| ID | SPEC-005 |
| Status | Accepted |
| Phase | A.2.6 |
| Component | Transport |
| Depends on | [SPEC-000](design-principles.md), [SPEC-001](sdk-client.md), [SPEC-002](configuration.md), [SPEC-003](authentication.md), [SPEC-004](tls.md) |
| Implementation | Not implemented |

## Status

Accepted — target architecture, not yet implemented. This specification has been
reviewed against the [Review Criteria](README.md#review-criteria) in
[Design Specifications](README.md) and is binding for implementation; see the
status model in [Design Specifications](README.md). A small number of questions
this specification would normally answer are, deliberately, left open — see
[Open Questions](#open-questions).

## Purpose

`Transport` is where [Configuration](configuration.md), [Authentication](authentication.md),
and [TLS](tls.md) — three components that until now have only been described as
inert, represented *information* — are first brought together and actually used to
communicate with LogRhythm over HTTP. It is the SDK's single HTTP boundary: API
modules never talk to an HTTP library directly, and never construct their own HTTP
clients (see [Component Model](../architecture/components.md), "API clients... never
construct an HTTP client themselves").

`Transport`:

- executes HTTP requests and produces responses.
- centrally applies authentication, TLS, and header behavior, so no API module has
  to.
- does not contain API-specific logic, parsing, or business logic of any kind.

## Scope

**In scope:**

- The role and responsibilities of the transport layer.
- The `HttpTransport` / `TransportProtocol` architecture and what it encapsulates.
- URL resolution from relative, API-module-supplied paths.
- HTTP client construction, pooling, and ownership.
- How authentication (SPEC-003) and TLS (SPEC-004) configuration are applied.
- Header layering and precedence.
- Timeout categories.
- Response handling: status code treatment, the SDK-internal response
  representation, and JSON handling.
- The categories of error `Transport` produces.
- What logging and debug metadata `Transport` makes available — not what is
  actually logged.
- The central redaction requirement applied before any of that metadata could be
  logged.
- Testability requirements.

**Out of scope** (referenced only; defined by their own future specifications, or
explicitly deferred — see [Non-Goals](#non-goals) and
[Future Extensions](#future-extensions)):

- API models.
- Parsers.
- Business logic.
- Logging implementation (which of the metadata `Transport` provides is actually
  written where, and in what format).
- The SDK's exception hierarchy (exact exception class names/types).
- Retry strategies.
- Streaming.
- Asynchronous transport.
- Concrete API endpoints.

## Responsibilities

`Transport`:

- executes HTTP requests on behalf of API modules and returns an SDK-internal
  response (see [Response Handling](#response-handling)).
- resolves relative, API-module-supplied paths into absolute URLs centrally (see
  [URL Resolution](#url-resolution)).
- constructs, pools, and owns (or does not own — see
  [HTTP Client Management](#http-client-management)) the underlying HTTP client(s).
- applies authentication centrally, so API modules never have to (see
  [Authentication Integration](#authentication-integration)).
- applies TLS configuration when establishing connections (see
  [TLS Integration](#tls-integration)).
- applies default and layered headers (see [Header Management](#header-management)).
- enforces timeouts on every request; no request is unbounded (see
  [Timeout Handling](#timeout-handling)).
- categorizes errors (connection, timeout, HTTP-level) for later translation into
  SDK exceptions (see [Error Behaviour](#error-behaviour)).
- makes logging and debug metadata available, already passed through central
  redaction (see [Logging Metadata](#logging-metadata),
  [Debug Metadata](#debug-metadata), and [Redaction](#redaction)).
- is testable without any real network access (see [Testability](#testability)).

## Non-Responsibilities

`Transport`:

- does not define API models.
- does not parse domain data or apply business logic.
- does not decide what is actually logged, or in what format — only what metadata is
  available (see [Logging Metadata](#logging-metadata)).
- does not define the SDK's exception classes or hierarchy — only error categories
  (see [Error Behaviour](#error-behaviour)).
- does not retry failed requests (see [Non-Goals](#non-goals)).
- does not stream request or response bodies (see [Non-Goals](#non-goals)).
- does not provide an asynchronous API (see [Non-Goals](#non-goals)).
- has no knowledge of concrete API endpoints — it only knows relative paths handed
  to it by API modules.

## Transport Model

**Decision: version 1 uses [httpx](https://www.python-httpx.org/) as the underlying
HTTP library** — see
[ADR-0006](../adr/0006-httpx-transport.md) for the full decision and its
alternatives. API modules must never depend on httpx directly, at any point —
they depend exclusively on the SDK's own transport abstraction.

**Decision: the SDK owns a dedicated `HttpTransport`.** It fully encapsulates:

- URL resolution
- headers
- authentication
- TLS
- timeouts
- error translation (categorization; see [Error Behaviour](#error-behaviour))
- request execution
- response construction

**Decision: `HttpTransport` implements a narrow `TransportProtocol`.** API modules
depend exclusively on this protocol/contract — never on `HttpTransport`'s concrete
implementation, and never on httpx. This is a direct application of
[SPEC-000](design-principles.md#architecture-principles)'s "Stable abstractions"
principle, which already anticipated exactly this: "the future transport and HTTP
architecture, where the concrete HTTP client is expected to sit behind such a
contract." It is not a new principle invented here, only its concrete application.

This is consistent with `HTTP Transport` as already named in
[Component Model](../architecture/components.md) as one of the three shared
infrastructure components [SPEC-001](sdk-client.md) creates or accepts via
dependency injection. `HttpTransport`/`TransportProtocol` **is** that component,
elaborated; this specification does not introduce a second, competing transport
component. [Component Model](../architecture/components.md) explicitly left the
transport library undecided ("It does not define... the transport library — those
are separate, future design specifications"); this specification is that decision.

No Python class definitions, method signatures, or attributes are given here —
consistent with every other specification in this series.

## URL Resolution

- **URL resolution happens exclusively in `Transport`.** API modules never
  construct, or receive, an absolute URL themselves.
- **API modules supply only relative endpoint paths.** Absolute URLs from an API
  module are not accepted.
- The base (host, and other connection information from
  [SPEC-002](configuration.md#configuration-model)'s "Connection information" group)
  is combined with the relative path to produce the actual request URL.
- The allowed endpoint scheme is governed by
  [ADR-0008](../adr/0008-require-https-for-sdk-managed-endpoints.md). `Transport`
  receives an already-validated HTTPS origin and does not silently rewrite an
  unsupported scheme.
- **Query parameters are handled structurally** — as a structured mapping the caller
  supplies, not as a manually concatenated string. `Transport` is responsible for
  correct encoding.

## HTTP Client Management

**Ownership** (binding, not an open question):

- An HTTP client `Transport` creates internally is owned by `LogRhythmClient` —
  exactly the same create-vs-inject rule
  [SPEC-001](sdk-client.md#ownership) already establishes for `HTTP Transport` as a
  whole, applied one level deeper, to the underlying HTTP client `HttpTransport`
  wraps.
- An HTTP client supplied externally (dependency injection) remains entirely owned
  by the caller who supplied it.
- **`HttpTransport` itself never independently owns the HTTP client.** It uses one,
  but ownership always resolves to either `LogRhythmClient` (if created internally)
  or the external caller (if injected) — never to `HttpTransport` as an independent
  third owner. This is consistent with, and does not contradict,
  [SPEC-001](sdk-client.md#ownership)'s existing rule that ownership is decided per
  component, at the time each component is obtained.

**Pooling** (binding, not an open question):

- Version 1 uses long-lived HTTP client instances internally — not one new client
  per request.
- Client pooling happens **per unique transport profile**. A transport profile
  consists of, at minimum: scheme, host, port, and TLS configuration.
- API modules never create their own HTTP clients (see
  [Component Model](../architecture/components.md)).

**Environment isolation** (binding, not an open question):

- `Transport` ignores the underlying HTTP library's own environment-variable-based
  configuration by default — conceptually equivalent to disabling that library's
  "trust environment" behavior. The SDK's own `Configuration` always takes
  precedence over ambient environment state. This is consistent with
  [SPEC-000](design-principles.md#architecture-principles)'s "Explicit over
  implicit" principle and [SPEC-000](design-principles.md#non-goals)'s "Implicit
  configuration" non-goal.

How exactly `HttpTransport` receives the relevant parts of `Configuration`
(connection, authentication, TLS) at construction time — the whole resolved
`Configuration`, or already-extracted values — is an implementation detail not
decided at this architectural level, consistent with this specification series not
defining Python signatures.

## Authentication Integration

- `Transport` centrally sets the `Authorization: Bearer <token>` header, using the
  bearer token [SPEC-003](authentication.md) establishes as version 1's
  authentication mechanism.
- **API modules never set this header themselves.** Authentication is applied
  exclusively by `Transport`, consistent with
  [SPEC-003](authentication.md#integration-with-logrhythmclient): `LogRhythmClient`
  and API modules never handle authentication information directly — only
  `Transport` acts on it. This is the future Transport specification
  [SPEC-003](authentication.md#purpose) already pointed to for "actually attaching
  that information to a request."
- Whether the bearer token is actually accepted by LogRhythm is only discoverable by
  making a real request — `Transport` does not pre-validate it. See
  [Validation](#validation) and [Error Behaviour](#error-behaviour); this is the
  same "future Authentication/Transport specification" boundary
  [SPEC-002](configuration.md#validation) and
  [SPEC-003](authentication.md#validation) already deferred server-side validation
  to.

## Header Management

Headers are applied in layers, from least to most specific:

```text
SDK default headers
    ↓
API-specific headers
    ↓
Request-specific headers
```

- **Normal headers may be overridden** by a more specific layer.
- **Security-critical headers (e.g. `Authorization`) must never be unintentionally
  overridden** by a later layer — accidental clobbering of authentication by an
  API-specific or request-specific header is not permitted.
- `Accept: application/json` is set by default.
- `Content-Type` is set only when the request actually has a JSON body — not
  unconditionally.

## TLS Integration

- `Transport` applies the TLS-related configuration
  [SPEC-004](tls.md#tls-model) already defines (verification mode, trust source,
  minimum TLS version) when constructing/pooling HTTP clients (see
  [HTTP Client Management](#http-client-management)).
- This specification does not redefine any TLS decision — it only describes that
  `Transport` is where those already-decided settings are applied. The exact
  cryptographic/handshake mechanics remain outside architecture-level scope,
  consistent with [SPEC-004](tls.md#non-goals) ("Cryptography implementation").
- The insecure-mode warning [SPEC-004](tls.md#certificate-verification) requires "at
  client creation or transport initialization" is, concretely, emitted at transport
  initialization — this specification does not change that requirement, only notes
  where it is satisfied.

## Timeout Handling

- Version 1 supports four timeout categories: **connect**, **read**, **write**, and
  **pool**.
- Timeouts are **active by default** — there is no unbounded/infinite request.
- The concrete default values for each category are an
  [Open Question](#open-questions); that timeouts exist, are categorized this way,
  and are never absent, is not.

## Response Handling

**Status codes:**

| Range | Treatment |
| --- | --- |
| `2xx` | Success. |
| `3xx` | Treated as an error — version 1 does not follow redirects by default (see below), so a redirect response is not a normal outcome. |
| `4xx` / `5xx` | Recognized as HTTP-level errors by `Transport`; translated into SDK exceptions later, by a future exception-handling specification (see [Error Behaviour](#error-behaviour)). |

**Redirects:** version 1 does not follow redirects by default, and version 1 does
not offer a way to change that — configurable redirect-following is a possible
[Future Extension](#future-extensions), not part of version 1.

**Response model:** `Transport` returns an SDK-internal response representation —
never the underlying HTTP library's response object directly. API modules perform
JSON mapping and model conversion themselves, from that SDK-internal representation
(see [Non-Goals](#non-goals) — model conversion is not `Transport`'s job).

**JSON handling:**

- JSON is processed explicitly by `Transport`.
- Invalid/malformed JSON in a response body produces an appropriate SDK-level error
  later (see [Error Behaviour](#error-behaviour)) — it is not silently ignored or
  passed through as if valid.
- An empty response body is **not** automatically interpreted as JSON (e.g. as
  `null` or an empty object) — emptiness and "valid empty JSON" are treated as
  distinct.

## Error Behaviour

This specification describes error categories conceptually. It does **not** define
exception class names or a class hierarchy — that belongs to a future
exception-handling specification, consistent with
[SPEC-001](sdk-client.md#public-api),
[SPEC-002](configuration.md#error-behaviour),
[SPEC-003](authentication.md#validation), and
[SPEC-004](tls.md#error-behaviour), all of which defer exception naming the same
way.

Categories `Transport` recognizes:

- **Connection failures** — e.g. DNS resolution failure, connection refused, TLS
  handshake failure.
- **Timeout errors** — one per category in
  [Timeout Handling](#timeout-handling) (connect, read, write, pool).
- **Unexpected redirect** — a `3xx` response, which version 1 treats as an error
  rather than following it (see [Response Handling](#response-handling)).
- **HTTP-level errors** — `4xx` / `5xx` responses.
- **Response body errors** — invalid/malformed JSON where JSON was expected (see
  [Response Handling](#response-handling)).

`Transport` categorizes; it does not retry (see [Non-Goals](#non-goals)) and does
not swallow errors — every category propagates to the caller, consistent with
[SPEC-000](design-principles.md#implementation-principles)'s "Fail fast" principle.

## Logging Metadata

`Transport` makes the following metadata **available**, at minimum:

- HTTP method
- endpoint
- sanitized query string
- status code
- duration
- error category (see [Error Behaviour](#error-behaviour))
- SDK request ID (`request_id`)
- server request ID (`server_request_id`), when returned by LogRhythm — tracked
  separately from the SDK request ID, never merged (see
  [SPEC-006, Request IDs](logging.md#request-ids))
- retry counter (reserved for the future retry extension; always present, even
  though version 1 has no retries — see [Non-Goals](#non-goals))

**`Transport` does not decide what is actually logged.** That decision belongs
exclusively to a future logging specification (SPEC-006) — consistent with
[SPEC-000](design-principles.md#documentation-principles)'s separation between what
a component represents/provides and what another component decides to do with it,
already applied throughout this series (e.g.
[SPEC-004](tls.md#configuration-integration) representing TLS settings without
enforcing them). All metadata `Transport` makes available has already passed
through central redaction — see [Redaction](#redaction).

## Debug Metadata

Beyond [Logging Metadata](#logging-metadata), `Transport` additionally makes
available, for debugging purposes:

- the full resolved endpoint (see [URL Resolution](#url-resolution))
- sanitized headers
- sanitized query string
- sanitized request body
- sanitized response body
- the active TLS mode
- the active timeout configuration
- how the URL was resolved

As with logging metadata, **whether any of this is actually emitted anywhere is
decided exclusively by a future logging specification**, not by `Transport`. Every
item listed here is already sanitized by central redaction (see
[Redaction](#redaction)) before it is made available at all.

## Redaction

`Transport` uses a **central redaction component from `core`** — not a
transport-local one — consistent with
[SPEC-000](design-principles.md#extensibility)'s "Shared infrastructure belongs in
`core`" principle. This introduces `Redaction` as a `core` utility; it is not yet
drawn in [Component Model](../architecture/components.md), which is intentionally a
high-level sketch, not an exhaustive enumeration of every `core` utility.

This component sanitizes, before anything is made available for potential logging
(see [Logging Metadata](#logging-metadata) and [Debug Metadata](#debug-metadata)),
at minimum:

**Headers:**

- `Authorization`
- `Cookie`
- `Set-Cookie`
- `Proxy-Authorization`
- `X-API-Key`
- `X-Auth-Token`

**Query parameters:**

- `token`
- `access_token`
- `apikey`
- `api_key`
- `password`
- `secret`
- `authorization`

This list is **not** closed — further additions remain possible. `Redaction` is
intended to be reused by a future Logging specification and a future exception
specification as well, not reimplemented per component — again per
[SPEC-000](design-principles.md#extensibility).

## Validation

`Transport` performs **no additional local validation** of `Configuration`,
`Authentication`, or TLS values beyond what
[SPEC-002](configuration.md#validation), [SPEC-003](authentication.md#validation),
and [SPEC-004](tls.md#validation) already perform during `Configuration`
resolution — `Transport` does not duplicate those checks.

The one thing `Transport` itself enforces structurally is
[URL Resolution](#url-resolution)'s rule that API modules supply only relative
paths — an absolute URL from an API module is rejected, not silently accepted.

Everything beyond local validation — whether a credential is actually accepted,
whether a host is actually reachable, whether a certificate is actually trusted by
the server — is discoverable only by executing a real request, and surfaces through
[Error Behaviour](#error-behaviour), not through a separate validation step.

## Testability

- `Transport` must be fully testable without real network access, consistent with
  [SPEC-000](design-principles.md#testability) ("Mockable infrastructure").
- Because API modules depend only on `TransportProtocol` (see
  [Transport Model](#transport-model)), tests can substitute a fake or mock
  transport without needing httpx, or any network, at all.
- Redaction (see [Redaction](#redaction)) must itself be testable — a test must be
  able to assert that a header or query parameter on the redaction lists never
  appears in the metadata `Transport` makes available.
- Timeout, error-categorization, and status-code-treatment behavior must be testable
  using simulated/mocked responses, without a live LogRhythm instance.
- No real credentials, hosts, or certificates are used in this specification or in
  any test; placeholders only.

## Examples

Pseudocode only — illustrative of intended usage, not a committed API surface, not a
real implementation, and not a claim about any concrete field name or httpx API
detail. Placeholder values only; no real credentials or hosts.

**An API module using `TransportProtocol` (never httpx, never an absolute URL):**

```python
response = transport.request(
    method="GET",
    path="some/relative/endpoint",  # relative only; Transport resolves the URL
    query=...,  # structured query parameters, not a manually built string
)
# `response` is Transport's SDK-internal response representation, not an httpx
# response. The API module converts it to models itself.
```

**`Transport` construction is internal to `LogRhythmClient` by default:**

```python
client = LogRhythmClient(configuration)
# LogRhythmClient creates and owns HttpTransport internally, using the relevant
# parts of `configuration` (connection, authentication, TLS).
```

**Dependency injection for tests (a fake transport, no httpx involved):**

```python
client = LogRhythmClient(
    configuration=test_configuration,
    logger=fake_logger,
    transport=fake_transport,  # implements TransportProtocol; owned by the caller
)
```

## Open Questions

These are explicitly undecided. They must not be resolved silently by
implementation; each requires an explicit decision (and, where architecturally
significant, an ADR) before it can move out of this list.

- **Concrete timeout default values.** The actual numeric defaults for connect,
  read, write, and pool timeouts (see [Timeout Handling](#timeout-handling)).
- **Response size limits.** Whether `Transport` enforces any limit on response body
  size.
- **Maximum redirect count.** Only relevant if/when configurable redirect-following
  becomes a supported [Future Extension](#future-extensions) — not applicable to
  version 1, which does not follow redirects at all (see
  [Response Handling](#response-handling)).

The "how is a correlation/request ID determined" question previously listed here
is settled by [SPEC-006](logging.md#request-ids): the SDK always generates its own
request ID locally, regardless of whether LogRhythm supplies one; a server-supplied
ID is tracked separately, and optionally, as `server_request_id`.

## Future Extensions

These are possible ideas for later, explicitly non-binding, and do not represent any
architectural decision or part of SPEC-005:

- Asynchronous transport.
- Streaming.
- Retries.
- HTTP/2.
- Proxy support.
- Configurable redirects.
- Configurable connection limits.

## Non-Goals

This specification, and by extension `Transport` itself, explicitly does not cover:

- API models.
- Parsers.
- Business logic.
- Logging implementation.
- Exception classes / the exception hierarchy.
- Retry strategies.
- Streaming.
- Asynchronous transport.
- Concrete API endpoints.

## References

- [SPEC-000 — Design Principles](design-principles.md)
- [SPEC-001 — SDK Client](sdk-client.md)
- [SPEC-002 — Configuration](configuration.md)
- [SPEC-003 — Authentication](authentication.md)
- [SPEC-004 — TLS](tls.md)
- [Architecture Overview](../architecture/overview.md)
- [Component Model](../architecture/components.md)
- [ADR-0006 — Use HTTPX as HTTP transport library](../adr/0006-httpx-transport.md) —
  the HTTP library decision [Transport Model](#transport-model) relies on.
