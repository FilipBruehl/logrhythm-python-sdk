# SPEC-010 — API Modules

| Field | Value |
| --- | --- |
| ID | SPEC-010 |
| Status | Accepted |
| Phase | A.2.11 |
| Component | API Modules |
| Depends on | [SPEC-000](design-principles.md), [SPEC-001](sdk-client.md), [SPEC-002](configuration.md), [SPEC-003](authentication.md), [SPEC-004](tls.md), [SPEC-005](transport.md), [SPEC-006](logging.md), [SPEC-007](exceptions.md), [SPEC-008](models.md), [SPEC-009](filters-and-options.md) |
| Implementation | Not implemented |

## Status

Accepted — target architecture, not yet implemented. This specification has been
reviewed against the [Review Criteria](README.md#review-criteria) in
[Design Specifications](README.md) and is binding for implementation; see the
status model in [Design Specifications](README.md). A small number of questions
this specification would normally answer are, deliberately, left open — see
[Open Questions](#open-questions).

## Purpose

This is the last piece of the architecture framework: it defines how the SDK's API
areas — `LogRhythmClient`'s children — are structured, obtained, and used. Every
prior specification in this series described a piece of shared infrastructure
(`Configuration`, `Authentication`, `TLS`, `Transport`, `Logging`, `Exceptions`,
`Models`, and the filter/pagination/sorting/options layer). `API Modules` is where
those pieces are finally assembled into the thing a caller actually touches.

**`LogRhythmClient` is the SDK's single primary entry point.** Every API area is
used exclusively through it:

```python
with LogRhythmClient.from_config("config.toml") as client:
    client.admin.hosts.list()
```

(The configuration file extension above is illustrative only — the concrete file
format remains an open question in [SPEC-002](configuration.md#open-questions), not
decided here.) Directly constructing an individual API client or `Resource` is not
the regular way a caller uses the SDK — see [Public API](#public-api).

## Scope

**In scope:**

- The seven supported API modules and their implementation order.
- The client/resource object hierarchy.
- How resources are organized on disk.
- Dependency injection into API clients and resources.
- API-level configuration (enabling/disabling an API area, path overrides).
- Lifecycle (eager construction, no network access at startup).
- The public, high-level API surface.
- The separately namespaced, lower-level "raw" API.
- Endpoint method naming and signature conventions.
- Return value conventions.
- The division of logging responsibility between `Transport` and resources.
- Why API modules never depend on each other directly.
- Public export conventions.
- Versioning posture.
- Feature detection posture.
- How future endpoint implementation work relates to the API Coverage Matrix.
- Testing strategy for endpoint implementations.

**Out of scope** (referenced only; defined by their own future specifications, or
explicitly deferred — see [Non-Goals](#non-goals) and
[Future Extensions](#future-extensions)):

- Concrete endpoints.
- Request/response models (see [SPEC-008](models.md)).
- Business logic.
- HTTP implementation (see [SPEC-005](transport.md)).
- Transport details.
- Logging details (see [SPEC-006](logging.md)).
- Exception implementation (see [SPEC-007](exceptions.md)).

## Responsibilities

**`LogRhythmClient`** is responsible for:

- being the composition root (see [SPEC-001](sdk-client.md#ownership)).
- its own lifecycle.
- holding `Configuration`.
- holding the central `Logger`.
- holding `Transport`.
- creating every API client.

**API clients** are responsible for:

- grouping their `Resource` objects.
- their API area's default path (see [API Paths](#api-paths)).
- passing shared infrastructure down to their resources.

**Resources** are responsible for:

- endpoint methods.
- relative endpoint paths.
- request/response models (see [SPEC-008](models.md)).
- filters, pagination, sorting, and options (see
  [SPEC-009](filters-and-options.md)).
- mapping a response onto typed models.

## Non-Responsibilities

**`LogRhythmClient`** is not responsible for:

- endpoint logic.
- HTTP.
- business logic.

**API clients** are not responsible for:

- HTTP.
- logging configuration.
- endpoint implementation.

**Resources** are not responsible for:

- HTTP.
- logger configuration.
- TLS.
- authentication.
- transport initialization.

## Supported APIs

**Decision: the SDK has exactly seven API modules.** Implementation order:

1. Administration API
2. AI Engine Cache Drilldown API
3. Metrics API
4. AI Engine API
5. Alarm API
6. Case API
7. Search API

**Public namespaces:**

```text
client.admin
client.drilldown
client.metrics
client.aie
client.alarms
client.cases
client.search
```

**Classes:**

```text
AdminApiClient
AieDrilldownApiClient
MetricsApiClient
AieApiClient
AlarmApiClient
CaseApiClient
SearchApiClient
```

**These seven remain the complete, unchanged set of vendor API areas.**
`client.raw` (see [Raw API](#raw-api)) is explicitly **not** an eighth API
module — it is a technical, advanced facade over the existing `Transport`, not
one of the seven vendor API areas above, not part of their implementation order,
not a substitute for a high-level endpoint implementation, and not counted as its
own vendor area in [API Coverage](#coverage).

**Consistency note:** several existing documents (`README.md`, `docs/vision.md`,
`CLAUDE.md`, `docs/coverage/api-coverage.md`, and
[Component Model](../architecture/components.md)) previously described five
planned API areas (Administration, AI Engine, Metrics, Alarm, Search), predating
this decision. Because leaving those unchanged would visibly contradict this
specification's now-binding count and order of seven, they have been updated in
this same change to reflect the same seven areas, in the same order — a minimal,
necessary consistency fix, not a new decision beyond what is stated here.

## Client Hierarchy

**Decision: the object structure is:**

```text
LogRhythmClient
└── API Client
    └── Resource
        └── Endpoint Methods
```

API clients group **only** resources. Resources contain **only** endpoint methods.
Neither layer is a place for anything else — see
[Responsibilities](#responsibilities) and [Non-Responsibilities](#non-responsibilities).

## Resource Hierarchy

**Decision: resources are organized by business area**, following
[SPEC-008](models.md#model-organisation)'s and
[SPEC-009](filters-and-options.md#resource-specific-models)'s existing "no large
collection files" principle, extended to resources themselves. Conceptually:

```text
admin/
    client.py

    hosts/
        resource.py
        models/
        filters/
        sorting/
        options/

    entities/
        ...

    log_sources/
        ...
```

**Pagination is deliberately not one of these per-resource folders.** The shared,
`core`-level `PaginationModel` is the standard, used by nearly all documented
endpoints (see [SPEC-009, Pagination](filters-and-options.md#pagination)). In the
rare, documented exception where a resource genuinely needs a different
pagination mechanism, the resulting resource-specific pagination model is placed
under that resource's own `models/` (shown above) — see
[SPEC-009, Resource-Specific Models](filters-and-options.md#resource-specific-models).
No separate `pagination/` folder is introduced, since a standard folder for this
case would misrepresent the exception as the norm.

## Dependency Injection

**API clients receive, at minimum:**

- `Configuration`
- `TransportProtocol` (see [SPEC-005](transport.md#transport-model))
- a child `Logger` (see [SPEC-006](logging.md#logger-hierarchy))

**Resources receive:**

- `TransportProtocol`
- a resource-level `Logger`
- API-level configuration (see [API Configuration](#api-configuration))

**No resource ever constructs, itself:**

- an HTTP client
- a logger
- authentication
- TLS
- transport

This is the same create-vs-inject boundary [SPEC-001](sdk-client.md#ownership) and
[Component Model](../architecture/components.md) already establish for
`LogRhythmClient`'s relationship to shared infrastructure, extended one level
further down the object graph.

## API Paths

**Decision: every API client defines a documented default path.**
Conceptually, `DEFAULT_API_PATH`.

**Path resolution order:**

1. an explicit path from `Configuration`, if supplied.
2. otherwise, the API client's documented default path.

**Default paths may only be taken from official LogRhythm documentation.** No
placeholder path is invented — consistent with
[SPEC-000](design-principles.md#api-design)'s "No invented API functionality"
principle.

## API Configuration

**Decision: API areas are enabled through `Configuration`.** Conceptually:

```yaml
apis:
  admin:
    enabled: true
    path: ...

  search:
    enabled: false
```

**Every API client always exists** — see [Client Hierarchy](#client-hierarchy) and
[Lifecycle](#lifecycle). An API area that is not configured, or explicitly
disabled, produces a local `ApiNotConfiguredError` when used — **without any
network access.**

**Decision: `ApiNotConfiguredError` is a `ClientStateError`, not a
`ConfigurationError`.** Conceptual hierarchy:

```text
LogRhythmSdkError
└── ClientStateError
    └── ApiNotConfiguredError
```

The overall `Configuration` can be entirely valid while a single API area is still
missing or disabled — the failure is not about `Configuration` being invalid, it
is about the state of one API client at the moment it is used. It only becomes
observable when that API area is actually accessed, not while `Configuration` is
being resolved. This makes it a local state error of the API client, consistent
with [SPEC-007](exceptions.md#client-state-errors)'s existing framing of
`ClientStateError` as covering "invalid use of `LogRhythmClient` itself,
independent of any particular request." [SPEC-007](exceptions.md#client-state-errors)
already frames its listed subclasses as a **minimum**, not an exhaustive set, so
adding `ApiNotConfiguredError` here does not contradict it — this specification
does not otherwise modify [SPEC-007](exceptions.md)'s hierarchy.

**Two distinct states, both handled by the same `ApiNotConfiguredError`:**

- **Not configured** — the API area's entry is entirely absent from
  `Configuration`. Conceptually: `configured = false`, `enabled = false`.
- **Explicitly disabled** — the API area's entry is present, but disabled.
  Conceptually: `configured = true`, `enabled = false`.

**For both states, identically:**

- the API client and its namespace exist (see [Lifecycle](#lifecycle)).
- resource objects may exist too.
- an endpoint call fails locally.
- no network access occurs.
- `ApiNotConfiguredError` is raised.

**No separate exception type exists for the two states.** The exception may carry
structured context distinguishing them, for example:

- `api_name`
- `configured`
- `enabled`
- `operation`

**No automatic activation** — an API area is never silently enabled as a side
effect of being used.

## Lifecycle

**Decision: every API client is constructed eagerly**, as part of
`LogRhythmClient` construction. Eager construction performs:

- **no** network access.
- **no** feature detection.
- **no** authentication.
- **no** API calls.

Construction builds **only** the object graph — nothing observable happens over
the network as a result of creating a `LogRhythmClient`, consistent with
[SPEC-000](design-principles.md#implementation-principles)'s "No network access on
import" principle, applied here to client construction as well.

## Public API

Regular callers use **only** the high-level API:

```python
client.admin.hosts.list(...)
client.admin.hosts.get(...)
client.admin.entities.create(...)
```

**Decision: the high-level API returns exclusively:**

- domain models (see [SPEC-008](models.md)).
- immutable collections.
- result models (see [Return Values](#return-values)).
- `None`.

**Never:**

- an underlying HTTP library's response object.
- `HttpTransport` itself.
- any internal transport object.

**API clients and resources may be publicly typed** (a caller can reference their
types, e.g. in a type hint), **but constructing them directly is not part of the
regular public SDK contract** — the regular path is always through
`LogRhythmClient`. Tests may construct them in isolation; see
[Testability](#testability).

## Raw API

**Decision: the SDK additionally has a clearly separated, advanced namespace:**

```text
client.raw
```

**Purpose:** debugging, analysis, and edge cases outside documented resource
coverage.

**Decision: `client.raw` is not an eighth API module.** It is:

- a technical, advanced facade over the existing `Transport` — not a vendor API
  area.
- not part of the seven vendor API areas in [Supported APIs](#supported-apis).
- not part of their fixed implementation order.
- not a substitute for implementing a documented endpoint through the high-level
  API.
- not counted as its own vendor area in the [API Coverage Matrix](#coverage).

**The Raw API:**

- uses the same `Transport`.
- uses the same authentication.
- uses the same TLS configuration.
- uses the same timeouts.
- uses the same request IDs.
- uses the same redaction.
- uses the same logging infrastructure.

**It does not permit bypassing the security architecture:**

- no absolute URLs — only relative API paths, the same rule
  [SPEC-005](transport.md#url-resolution) already enforces.
- no arbitrary manipulation of security-critical headers (see
  [SPEC-005](transport.md#header-management)).

**The Raw API has explicitly weaker stability guarantees than the high-level API.**

## Endpoint Methods

**Naming — CRUD verbs where they genuinely apply:**

- `list`
- `get`
- `create`
- `update`
- `delete`

**Vendor-specific operations are preserved as-is** — they are not artificially
forced into CRUD naming:

```text
get_details()
get_details_and_items()
create_from_file()
get_display_names()
```

Method names stay Pythonic; they are not renamed to disguise what the vendor
operation actually does.

**Signatures:** a simple identifier may be positional. Every other parameter is
**keyword-only**:

```python
hosts.get(host_id)

hosts.list(
    *,
    filters=...,
    pagination=...,
    sorting=...,
)
```

## Return Values

**Single objects:** a typed response model (see [SPEC-008](models.md#response-models)).

**Lists:**

- a `tuple[...]`, for endpoints without documented paging metadata.
- a dedicated result model, for endpoints with documented paging information.

**Delete:**

- `None`, for an empty, successful response.
- a typed model, if the endpoint documents one.

**No `bool` return values.**

## Logging Responsibilities

**Decision: technical logs originate exclusively in `Transport`**, per
[SPEC-006](logging.md#transport-integration). **Resources log only domain-level
events**, per [SPEC-006](logging.md#api-module-logging).

**Resources must not duplicate:**

- URL
- duration
- status
- request start
- response receipt
- transport errors

— this is not a new rule; it restates
[SPEC-006](logging.md#api-module-logging)'s existing "must not duplicate" list for
API-module logging, applied here at the resource level specifically.

**Child logger example:**

```text
logrhythm_sdk.admin.hosts
```

## API Independence

**Decision: API modules never use each other directly.** Shared logic belongs
exclusively in `core` components — the same rule
[SPEC-000](design-principles.md#extensibility) ("Shared infrastructure belongs in
`core`") and [SPEC-009](filters-and-options.md#resource-specific-models) ("a
shared component belongs in `core` only when the semantics are actually shared")
already establish, applied here to API modules as a whole: **no implicit coupling
between API areas.**

## Public Exports

**Package root:**

```python
LogRhythmClient
LogRhythmSdkError
```

**API namespaces export their API clients.** **Resource namespaces export their
public models** (see [SPEC-008](models.md#public-api) and
[SPEC-009](filters-and-options.md#public-api)). **No mass exports** — the same
restraint [SPEC-007](exceptions.md#public-api),
[SPEC-008](models.md#public-api), and
[SPEC-009](filters-and-options.md#public-api) already apply to their own public
surfaces, applied here at the top level of the package.

## Versioning

**Decision: no version folders** (e.g. `v1/`) **exist unless and until the SDK
actually supports parallel API versions.** A precautionary version folder is not
created ahead of that need.

## Feature Detection

**No automatic feature detection.** **No network requests at SDK startup** — this
restates [Lifecycle](#lifecycle)'s eager-but-network-free construction rule; it is
not a separate decision.

## Coverage

**Decision: every future endpoint implementation requires, at minimum:**

- a documented HTTP method.
- a documented relative path.
- a request model.
- a response model.
- documented error behavior.
- a corresponding entry in
  [docs/coverage/api-coverage.md](../coverage/api-coverage.md).

**No endpoint is implemented on the basis of assumed CRUD semantics alone** —
consistent with [SPEC-000](design-principles.md#api-design)'s "No invented API
functionality" principle and
[docs/development/api-implementation-workflow.md](../development/api-implementation-workflow.md).

**Every SDK method must remain traceable to exactly one vendor endpoint.**

## Testing

Tests distinguish between:

- **documentation-based tests** — derived directly from official documentation.
- **example-based tests** — derived from real, documented request/response
  examples.
- **verified integration tests** — run against a real or sanctioned LogRhythm
  environment.

**Where no real request/response examples exist, no invented data is used.**
Synthetic fixtures may contain **only documented fields**, and must be clearly
marked as synthetic — consistent with
[SPEC-000](design-principles.md#api-design)'s "No invented API functionality" and
"Do not alter vendor behavior" principles, and the broader "do not invent
undocumented behavior" rule this whole series follows.

## Failure Behaviour

Using an API area that is not configured or is disabled (see
[API Configuration](#api-configuration)) fails immediately and locally as
`ApiNotConfiguredError`, per
[SPEC-000](design-principles.md#implementation-principles)'s Fail Fast principle
— never as a deferred, network-observable failure. Beyond that, this
specification introduces no new failure-handling rule: HTTP-, transport-, and
model-level failures continue to be governed by
[SPEC-005](transport.md#error-behaviour),
[SPEC-007](exceptions.md#exception-hierarchy), and
[SPEC-008](models.md#failure-behaviour) exactly as those specifications already
define.

## Testability

- Every layer described here must be testable without real network access,
  consistent with [SPEC-000](design-principles.md#testability).
- API clients and resources can be constructed directly and in isolation in
  tests, even though that is not the regular public usage path — see
  [Public API](#public-api).
- Dependency injection (see [Dependency Injection](#dependency-injection)) means a
  test can supply a fake `TransportProtocol` and logger to any API client or
  resource without needing `LogRhythmClient` itself.
- `ApiNotConfiguredError` (see [API Configuration](#api-configuration)) must be
  testable without network access — it is a local, immediate failure by
  definition.
- No real credentials, hosts, or production response data are used in this
  specification or in any test; placeholders only.

## Examples

Pseudocode only — illustrative of intended usage, not a committed API surface, not
a real implementation, and not a claim about any concrete field name or class
signature. Placeholder values only; no real credentials or hosts.

**The regular path — through `LogRhythmClient`:**

```python
with LogRhythmClient.from_config("config.toml") as client:
    hosts = client.admin.hosts.list(
        filters=HostFilter(has_login=True),
        pagination=Pagination(offset=0, count=25),
    )
    host = client.admin.hosts.get(host_id=42)
```

**A not-configured or disabled API area fails locally, without a network call:**

```python
with LogRhythmClient.from_config("config.toml") as client:
    client.search.query(...)
    # → ApiNotConfiguredError, whether `search` is absent from Configuration
    # entirely (not configured) or present but disabled (explicitly disabled) —
    # see API Configuration
```

**The Raw API — advanced, lower stability, same security architecture:**

```python
with LogRhythmClient.from_config("config.toml") as client:
    response = client.raw.get("admin/hosts", params={"count": 25})
    # relative path only; same transport, auth, TLS, redaction, and logging
```

## Open Questions

These are explicitly undecided. They must not be resolved silently by
implementation; each requires an explicit decision (and, where architecturally
significant, an ADR) before it can move out of this list.

- **Exact package names for individual resources.** The precise module layout
  beneath each API area beyond what [Resource Hierarchy](#resource-hierarchy)
  already shows conceptually.
- **Final shape of the Raw API.** Its exact method signatures and return type,
  beyond the constraints already fixed in [Raw API](#raw-api).
- **Possible shared result models.** Whether any result model (see
  [Return Values](#return-values)) turns out to be genuinely shared across API
  areas, versus resource-specific.
- **Future workflow/composite APIs.** Whether and how higher-level, multi-step
  operations might be introduced later (see
  [Future Extensions](#future-extensions)).

## Future Extensions

These are possible ideas for later, explicitly non-binding, and do not represent
any architectural decision or part of SPEC-010:

- Workflow APIs.
- Batch APIs.
- Asynchronous APIs.
- API discovery.
- Composite operations.
- Plugin APIs.
- Experimental low-level extensions.

## Non-Goals

This specification, and by extension the API module architecture itself,
explicitly does not cover:

- Business logic.
- HTTP implementation.
- Endpoint implementation.
- Transport implementation.
- Coupling between API modules (see [API Independence](#api-independence)).
- Automatic feature detection (see [Feature Detection](#feature-detection)).
- Network access at SDK startup (see [Lifecycle](#lifecycle)).
- Direct use of httpx by anything above `Transport` (see
  [Dependency Injection](#dependency-injection)).
- Artificial CRUD remapping of vendor-specific operations (see
  [Endpoint Methods](#endpoint-methods)).
- Bypassing the security architecture via the Raw API (see [Raw API](#raw-api)).

## References

- [SPEC-000 — Design Principles](design-principles.md)
- [SPEC-001 — SDK Client](sdk-client.md)
- [SPEC-002 — Configuration](configuration.md)
- [SPEC-003 — Authentication](authentication.md)
- [SPEC-004 — TLS](tls.md)
- [SPEC-005 — Transport](transport.md)
- [SPEC-006 — Logging](logging.md)
- [SPEC-007 — Exception Handling](exceptions.md)
- [SPEC-008 — Models](models.md)
- [SPEC-009 — Filters, Pagination, Sorting and Options](filters-and-options.md)
- [Architecture Overview](../architecture/overview.md)
- [Component Model](../architecture/components.md)
- [API Implementation Workflow](../development/api-implementation-workflow.md)
- [API Coverage Matrix](../coverage/api-coverage.md)
- No existing ADR (see [docs/adr/](../adr/README.md)) is specific to API module
  architecture; none is referenced here as directly applicable.
