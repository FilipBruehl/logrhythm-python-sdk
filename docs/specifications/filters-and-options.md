# SPEC-009 — Filters, Pagination, Sorting and Options

| Field | Value |
|---|---|
| ID | SPEC-009 |
| Status | Draft |
| Phase | A.2.10 |
| Component | Filters, Pagination, Sorting and Options |
| Depends on | [SPEC-000](design-principles.md), [SPEC-005](transport.md), [SPEC-007](exceptions.md), [SPEC-008](models.md) |
| Implementation | Not implemented |

## Status

Draft — target architecture only, not implemented. This specification has not yet
been reviewed against the [Review Criteria](README.md#review-criteria) in
[Design Specifications](README.md) and is not binding. No implementation may start
from this Draft; see the status model in [Design Specifications](README.md). A
small number of questions this specification would normally answer are,
deliberately, left open — see [Open Questions](#open-questions).

## Purpose

This specification covers everything a caller supplies to shape a request that is
**not** a request body: filters, pagination, sorting, and resource-specific
functional options. [SPEC-008](models.md) already defined the SDK's model
architecture in general — Pydantic v2, immutability, aliasing, strict validation —
and explicitly excluded this territory from its own scope. `Filters, Pagination,
Sorting and Options` is where that excluded territory gets its own architecture,
built on the same foundation.

A single, simple parameter — a resource ID, for example — is not part of this
specification's territory either: it is passed directly to an API method and never
needs a model of its own (see
[Separation from Request Models](#separation-from-request-models)).

## Scope

**In scope:**

- Shared model categories for filters, pagination, sorting, and options.
- The base hierarchy these categories build on.
- How they stay separated from [SPEC-008](models.md#request-models) request-body
  models.
- Resource-specific vs. shared (`core`) implementation.
- Query and header serialization, including multi-value handling.
- Empty/unset value handling.
- Date/time and enum handling, consistent with
  [SPEC-008](models.md#date-and-time).
- The concrete pagination model.
- The sorting model.
- Functional, resource-specific options.
- Conflict handling between models that would otherwise produce the same
  manufacturer parameter.
- Public export namespaces.
- Testability.

**Out of scope** (referenced only; defined by their own specifications, or
explicitly deferred — see [Non-Goals](#non-goals) and
[Future Extensions](#future-extensions)):

- Request-body models (see [SPEC-008](models.md#request-models)).
- Concrete API endpoints.
- Business logic.
- A generic query DSL.
- Free-form operator expressions.
- Raw query parameters.
- Technical, global `RequestOptions`.
- Concrete transport method signatures.
- Runtime implementation.

## Responsibilities

This specification:

- defines shared base categories — `FilterModel`, `PaginationModel`,
  `SortingModel`, `OptionsModel` — for everything a caller supplies beyond a
  request body (see [Base Models](#base-models)).
- keeps these categories strictly separate from
  [SPEC-008](models.md#request-models)'s request-body models (see
  [Separation from Request Models](#separation-from-request-models)).
- defines a common pagination model for the majority of documented endpoints (see
  [Pagination](#pagination)).
- defines a sorting model built on resource-specific, strict enums (see
  [Sorting](#sorting)).
- defines how these models serialize to query parameters or headers, including
  multi-value handling (see [Query Serialization](#query-serialization),
  [Header Serialization](#header-serialization), and
  [Multiple Values](#multiple-values)).
- detects and rejects conflicting parameter values locally, rather than silently
  resolving them (see [Conflict Handling](#conflict-handling)).
- keeps the public surface organized under stable, resource-specific (or, where
  genuinely shared, `core`) namespaces (see
  [Model Organisation](#model-organisation) and [Public API](#public-api)).

## Non-Responsibilities

This specification:

- does not define request-body models — see [SPEC-008](models.md#request-models).
- does not implement HTTP or transport logic — see [SPEC-005](transport.md#purpose).
- does not define concrete API endpoints or business logic.
- does not provide a generic filter expression language (see
  [No Generic Filter DSL](#no-generic-filter-dsl)).
- does not provide a way to send an undocumented, arbitrary parameter (see
  [No Raw Parameter Escape Hatch](#no-raw-parameter-escape-hatch)).
- does not define the exception hierarchy itself — conflicts and validation
  failures surface as [SPEC-007](exceptions.md#model-errors) exceptions, not
  something this specification defines independently.

## Model Categories

Four shared categories cover everything in this specification's scope:

- **Filters** — resource-specific criteria that narrow a list operation.
- **Pagination** — how many results, starting where (see
  [Pagination](#pagination)).
- **Sorting** — result ordering (see [Sorting](#sorting)).
- **Functional options** — resource-specific, documented behavioral toggles (see
  [Functional Options](#functional-options)) — never a technical, generic
  "options bag."

These are the categories a list-style API method accepts **in addition to** — and
strictly separate from — any request body (see
[Separation from Request Models](#separation-from-request-models)).

## Base Models

**Decision: all filter, pagination, sorting, and options models use Pydantic v2** —
the same foundation [SPEC-008](models.md#purpose) already establishes for the rest
of the SDK. No `dataclasses`. Every model is:

- **frozen**
- **keyword-only**
- **fully typed**
- **strictly validated**
- **documented**

**Decision: the base hierarchy stays deliberately small.** Conceptually:

```text
SdkModel
    ├── FilterModel
    ├── PaginationModel
    ├── SortingModel
    └── OptionsModel
```

Each base class carries **only** behavior genuinely common across that category —
not speculatively added. Resources define concrete models by inheriting from the
matching base class. **No deep or precautionary inheritance** — this is the same
"Composition over inheritance" / "No speculative abstractions" application
[SPEC-008](models.md#base-models) already makes for its own base hierarchy.

Because every model here is immutable (inherited from `SdkModel`, per
[SPEC-008](models.md#immutability)), a change always produces a new object.
Factory or helper methods for that (e.g. something like `with_changes(...)`) are
introduced **only where a concrete, present need exists** — there is no
precautionary, uniform method mandated across every model, the same restraint
[SPEC-008](models.md#immutability) already applies to itself. The concrete API for
this remains undecided — see [Open Questions](#open-questions).

## Separation from Request Models

**Decision: the following stay strictly separate:**

- request-body models (see [SPEC-008](models.md#request-models))
- filters
- pagination
- sorting
- functional options
- direct, simple method parameters

A single simple parameter (e.g. an ID) is passed directly — never wrapped in a
purpose-built model:

```python
client.admin.hosts.get(host_id=42)
```

A list-style operation, by contrast, receives filters/pagination/sorting as
separate, named arguments:

```python
client.admin.hosts.list(
    filters=HostFilter(...),
    pagination=Pagination(...),
    sorting=HostSorting(...),
)
```

## Resource-Specific Models

**Decision: filter, sorting, and functional option models are defined per business
resource.** For example:

```text
admin/
└── hosts/
    ├── filters/
    ├── sorting/
    └── options/
```

**Pagination may be a shared `core` model** when its semantics are genuinely
identical across APIs (see [Pagination](#pagination)). **A shared component
belongs in `core` only when the semantics are actually shared** — matching
parameter *names* across two APIs is not, by itself, sufficient justification;
this is the same standard [SPEC-000](design-principles.md#extensibility)'s "Shared
infrastructure belongs in `core`" principle already sets, applied here.

## Validation

**Decision: every filter, pagination, sorting, and options model is strict:**

- unknown fields are rejected.
- no free-form additional parameters are accepted.
- no automatic, loose type coercion occurs.
- only documented parameters are accepted.
- enums are strict (see [Enums](#enums)).
- no undocumented operators are accepted.

A validation failure surfaces as a [SPEC-007](exceptions.md#model-errors)
`ModelError` — consistent with how [SPEC-008](models.md#validation) already
routes model validation failures; this specification does not define a separate
error mechanism.

## Aliases

**Decision: manufacturer field names are mapped through explicit Pydantic
aliases** — the same rule [SPEC-008](models.md#aliases) already establishes for
every model. Examples:

- `orderBy` → `order_by`
- `entityIds` → `entity_ids`
- `hasLogin` → `has_login`

**No global alias-generation mechanism serves as the sole basis** for this mapping
— each alias remains explicit and reviewable, consistent with
[SPEC-008](models.md#aliases)'s identical rule.

## Serialization Responsibilities

The pipeline from a filled-in model to an actual HTTP request is:

```text
Pydantic model
    → validated dump, using manufacturer aliases
    → the Resource assigns the value(s) to an HTTP position
    → Transport encodes it for that position (query, header, or JSON)
```

**A Resource receives these models as separate, named arguments**, and decides
**which HTTP position** each one is used at:

```python
resource.list(
    filters=filters,
    pagination=pagination,
    sorting=sorting,
    options=options,
)
```

Possible positions:

- query parameters
- headers
- another position, only if documented

[Transport](transport.md#purpose) performs the actual technical encoding for
whichever position is used. **Models never construct a finished query string
themselves** — that is Transport's job, not a model's (see
[Query Serialization](#query-serialization)). The concrete transport method
signature that carries this handoff is **not** defined by this specification.

**Boundary with request bodies:** request-body models continue to serialize as
ordinary JSON structures, per [SPEC-008](models.md#serialization) — a body field
that happens to be a list or a mapping (e.g. `{"items": []}` or
`{"settings": {"enabled": true}}`) follows JSON serialization, not the
query/header rules this specification defines. The two must not be conflated.

## Query Serialization

**Decision: documented scalar query values are encoded in the form the
manufacturer expects.** One binding, known form:

```text
hasLogin=true
```

**Boolean values are serialized lowercase:**

```text
true
false
```

## Header Serialization

Where a resource documents that a filter, pagination, sorting, or options value is
expected as a header rather than a query parameter (see
[Serialization Responsibilities](#serialization-responsibilities)), the same
model — with the same aliasing ([Aliases](#aliases)) and strict validation
([Validation](#validation)) — is used; only the HTTP position differs. Headers are
**not** treated as, or encoded like, a JSON body (see
[Serialization Responsibilities](#serialization-responsibilities)).

The exact multi-value encoding convention for a value placed in a header (as
opposed to a query parameter — see [Multiple Values](#multiple-values)) is not
decided by this specification where it is not already documented by the vendor —
see [Open Questions](#open-questions).

## Multiple Values

**Decision: documented multi-value query parameters are serialized
comma-separated**, by default. Examples:

```text
entityIds=1,2
hasLogin=true,false
```

Which can produce a query string such as:

```text
entityIds=1,2&hasLogin=true,false
```

**Binding rules:**

- **No automatic repetition of the same query key** (i.e. not
  `entityIds=1&entityIds=2`).
- **No JSON array syntax in query parameters.**
- **No freely chosen alternative list serialization.**
- **Field-specific deviations require explicit documentation** — they are not
  assumed.

Internally, immutable sequences on these models should preferably be modeled as
tuples.

**This is distinct from request-body lists and dictionaries.** Those follow
[SPEC-008](models.md#serialization) and serialize as ordinary JSON structures
(e.g. `{"items": []}`) — that JSON-list semantics must not be confused with the
comma-separated query-list semantics defined here (see
[Serialization Responsibilities](#serialization-responsibilities)).

## Empty and Unset Values

**Decision: by default:**

- unset values are not sent.
- `None` is not sent.
- empty strings are not sent.
- empty sequences are not sent.

**Deviations are permitted only where the relevant API documentation defines an
explicit semantics for them.** A value must never be automatically turned into the
literal string `"None"`.

## Date and Time

Date/time values follow [SPEC-008](models.md#date-and-time) exactly — no separate
rule is introduced here:

- timezone-aware.
- internally UTC.
- naive values are rejected.
- serialized in the ISO format the specific endpoint requires.

**A shared date-range model is introduced only if multiple resources genuinely
share the same range semantics** — matching field names alone are not sufficient,
the same standard [Resource-Specific Models](#resource-specific-models) already
applies to shared `core` components generally.

## Enums

Enums remain strict in both directions, consistent with
[SPEC-008](models.md#enums), expected to be `StrEnum` and/or `IntEnum`.

**For sorting, documented sortable fields are modeled as resource-specific
enums** — not free strings — see [Sorting](#sorting). Unknown values produce local
validation failures, the same as everywhere else strict enums are used in this
series.

## Pagination

**Decision: version 1 uses a shared offset-based model for most documented
endpoints:**

```text
offset
count
```

**Binding semantics:**

- **`offset`**
  - starting point.
  - type `int`.
  - minimum `0`.
  - default `0`.
- **`count`**
  - number of objects to retrieve.
  - type `int`.
  - range `1` to `1000`.
  - default `25`.

**Further binding rules:**

- Pagination is immutable and strict (see [Base Models](#base-models)).
- It is only passed to endpoints that actually support pagination.
- Invalid values are rejected locally.
- Values are **never** silently corrected or clamped into range.
- Manufacturer naming is handled through explicit aliases (see
  [Aliases](#aliases)).
- A resource gets its own, different pagination model only where the API
  documents a genuinely different pagination mechanism.

**No precautionary cursor-, token-, or page-based pagination hierarchy exists in
version 1** — see [Future Extensions](#future-extensions) for where that
possibility is tracked instead.

## Sorting

**Decision: sorting uses its own model.** Conceptual (manufacturer) fields:

```text
orderBy
dir
```

Pythonic representation:

```text
order_by
direction
```

**Binding rules:**

- **`order_by`** uses a resource-specific, strict enum.
- **`direction`** uses a shared, strict enum. Typical directions are ascending and
  descending.
- Manufacturer values are defined explicitly as enum values (see
  [Aliases](#aliases)).
- **No free sort-field strings** where a closed set of sortable fields is
  documented.
- **Multi-field sorting is supported only where the API explicitly supports it.**

Example:

```python
HostSorting(
    order_by=HostSortField.NAME,
    direction=SortDirection.ASCENDING,
)
```

The exact manufacturer values for the sort-direction enum remain a detail
question wherever they are not already documented — see
[Open Questions](#open-questions).

## Functional Options

`OptionsModel` is a possible base class for resource-specific, functional options.
Examples that **may** exist, where documented:

- `include`
- `expand`
- `fields`
- `select`
- resource-specific header options

**Binding rules:**

- Introduced **only** where a documented need exists — never speculatively.
- **No generic, catch-all options class.**
- **No technical, global `RequestOptions`** (see [Non-Goals](#non-goals)).
- A closed set of documented values is modeled as a strict enum, the same as
  everywhere else (see [Enums](#enums)).
- The resource decides the HTTP position, per
  [Serialization Responsibilities](#serialization-responsibilities).

## Conflict Handling

**Decision: if more than one model would produce the same manufacturer parameter,
local assembly fails.** There is **no silent "last one wins" behavior.**

Example:

```text
Filter produces count=50
Pagination produces count=25
→ local failure
```

The concrete exception category follows [SPEC-007](exceptions.md#exception-hierarchy)
— this specification does not define a competing error mechanism. **Conflict
detection must be deterministic and testable offline** (see
[Testability](#testability)).

## No Generic Filter DSL

**Version 1 does not have:**

- AND/OR/NOT expression trees.
- operator overloading.
- freely nested filters.
- generic field operators.
- a query-builder DSL.

Multiple fields on one filter model represent **only** the documented server
semantics — nothing more general. **An implicit AND relationship between fields
may only be assumed where it is documented or independently verified** — never
guessed, consistent with
[SPEC-000](design-principles.md#api-design)'s "No invented API functionality"
principle.

## No Raw Parameter Escape Hatch

**Version 1 has no public mechanism like:**

```python
raw_query = {"undocumentedParameter": "value"}
```

New query or header parameters are added only after documented or verified
support, in a new SDK version. This is a deliberate consequence of:

- strict typing (see [Validation](#validation)),
- safe redaction (see [SPEC-005](transport.md#redaction) and
  [SPEC-006](logging.md#redaction) — an undocumented, arbitrary parameter could
  not reliably be redacted),
- a traceable public API, and
- [SPEC-000](design-principles.md#api-design)'s "No invented API functionality"
  principle.

## Model Organisation

Filter, sorting, and options models live under their resource, per
[Resource-Specific Models](#resource-specific-models) — for example
`admin/hosts/filters/`, `admin/hosts/sorting/`, `admin/hosts/options/`. Shared
pagination and sorting-direction components, where genuinely shared, live in
`core`, consistent with [SPEC-008](models.md#model-organisation)'s "no large
collection files" principle applied to this category of model as well.

The folder-level layout beneath a resource is shown concretely in
[SPEC-010 — Resource Hierarchy](api-modules.md#resource-hierarchy) (e.g.
`resource.py`, `models/`, `filters/`, `sorting/`, `options/`); finer detail below
that (module contents, class/file naming) is not decided here — see
[Open Questions](#open-questions).

## Public API

**Decision: resource-specific models are exported from stable resource
namespaces:**

```python
from logrhythm_sdk.admin.hosts.filters import HostFilter
from logrhythm_sdk.admin.hosts.sorting import HostSorting
```

**Shared models may be available from stable `core` namespaces:**

```python
from logrhythm_sdk.core.pagination import Pagination
from logrhythm_sdk.core.sorting import SortDirection
```

**No mass exports at the package root** — this is the same restraint
[SPEC-008](models.md#public-api) and [SPEC-007](exceptions.md#public-api) already
apply to their own public surfaces.

## Failure Behaviour

Validation and conflict detection (see [Validation](#validation) and
[Conflict Handling](#conflict-handling)) follow Fail Fast, consistent with
[SPEC-000](design-principles.md#implementation-principles) and
[SPEC-008](models.md#failure-behaviour): an invalid or conflicting set of models
is never partially assembled or silently resolved — failure is immediate and
explicit, surfacing as the corresponding [SPEC-007](exceptions.md#model-errors)
exception. This specification introduces no exception to Fail Fast.

## Testability

- Every model in this specification must be fully testable without real network
  access, consistent with [SPEC-000](design-principles.md#testability).
- Query and header serialization (see [Query Serialization](#query-serialization),
  [Header Serialization](#header-serialization), and
  [Multiple Values](#multiple-values)) must be testable in isolation, independent
  of a real Transport.
- Conflict detection (see [Conflict Handling](#conflict-handling)) must be
  deterministic and testable offline.
- Pagination bounds and defaults (see [Pagination](#pagination)) must be testable
  without a live LogRhythm instance.
- No real credentials, hosts, or production data are used in this specification or
  in any test; placeholders only.

## Examples

Pseudocode only — illustrative of intended usage, not a committed API surface, not
a real implementation, and not a claim about any concrete field name or class
signature. Placeholder values only.

**A list call combining filters, pagination, and sorting:**

```python
client.admin.hosts.list(
    filters=HostFilter(entity_ids=(1, 2), has_login=True),
    pagination=Pagination(offset=0, count=25),
    sorting=HostSorting(
        order_by=HostSortField.NAME,
        direction=SortDirection.ASCENDING,
    ),
)
```

**A single, simple parameter needs no model:**

```python
client.admin.hosts.get(host_id=42)
```

**A conflicting combination fails locally (illustrative only):**

```python
client.admin.hosts.list(
    filters=HostFilter(count=50),  # HostFilter also defines `count`
    pagination=Pagination(count=25),
)
# → local failure: both models would produce the manufacturer `count` parameter
```

## Open Questions

These are explicitly undecided. They must not be resolved silently by
implementation; each requires an explicit decision (and, where architecturally
significant, an ADR) before it can move out of this list.

- **Exact class and module names for the base types.** The concrete names behind
  `FilterModel`, `PaginationModel`, `SortingModel`, and `OptionsModel` (see
  [Base Models](#base-models)).
- **Module/file layout within each resource's `filters/`, `sorting/`, and
  `options/` folders.** The folder-level structure itself is decided (see
  [Model Organisation](#model-organisation) and
  [SPEC-010 — Resource Hierarchy](api-modules.md#resource-hierarchy)); what is not
  decided is the finer-grained layout within those folders.
- **Exact manufacturer values for the shared sort-direction enum**, where not
  already documented (see [Sorting](#sorting)).
- **Documented exceptions to the shared pagination model** — which specific
  endpoints, if any, require a different pagination mechanism (see
  [Pagination](#pagination)).
- **Functional header options and their base class** — the concrete shape of
  resource-specific header options (see
  [Functional Options](#functional-options) and
  [Header Serialization](#header-serialization)).
- **Endpoint-specific special cases for multi-value serialization** — where a
  documented endpoint deviates from the default comma-separated form (see
  [Multiple Values](#multiple-values)).

## Future Extensions

These are possible ideas for later, explicitly non-binding, and do not represent
any architectural decision or part of SPEC-009:

- Alternative pagination mechanisms.
- Cursor- or token-based pagination.
- Multi-field sorting (beyond what is already documented as supported).
- Generic filter expressions — only if a documented API genuinely supports them.
- An unstable, low-level client.
- Code generation from verified schemas.
- Property-based testing.
- Additional shared value objects.

## Non-Goals

This specification, and by extension the components it defines, explicitly does
not cover:

- Mixing with request-body models (see
  [Separation from Request Models](#separation-from-request-models)).
- Free-form raw parameters (see
  [No Raw Parameter Escape Hatch](#no-raw-parameter-escape-hatch)).
- A generic query DSL (see [No Generic Filter DSL](#no-generic-filter-dsl)).
- Operator overloading.
- Invented filter operators.
- Technical, global `RequestOptions`.
- Silent parameter conflicts (see [Conflict Handling](#conflict-handling)).
- Manual query-string construction by models (see
  [Serialization Responsibilities](#serialization-responsibilities)).
- A precautionary pagination hierarchy (see [Pagination](#pagination)).
- Mass exports at the package root (see [Public API](#public-api)).

## References

- [SPEC-000 — Design Principles](design-principles.md)
- [SPEC-005 — Transport](transport.md)
- [SPEC-007 — Exception Handling](exceptions.md)
- [SPEC-008 — Models](models.md)
- [Architecture Overview](../architecture/overview.md)
- [Component Model](../architecture/components.md)
- No existing ADR (see [docs/adr/](../adr/README.md)) is specific to filter,
  pagination, sorting, or options architecture; none is referenced here as
  directly applicable.
