# SPEC-008 — Models

| Field | Value |
| --- | --- |
| ID | SPEC-008 |
| Status | Draft |
| Phase | A.2.9 |
| Component | Models |
| Depends on | [SPEC-000](design-principles.md), [SPEC-001](sdk-client.md), [SPEC-002](configuration.md), [SPEC-003](authentication.md), [SPEC-005](transport.md), [SPEC-006](logging.md), [SPEC-007](exceptions.md) |
| Implementation | Not implemented |

## Status

Draft — target architecture only, not implemented. This specification has not yet
been reviewed against the [Review Criteria](README.md#review-criteria) in
[Design Specifications](README.md) and is not binding. No implementation may start
from this Draft; see the status model in [Design Specifications](README.md). A
small number of questions this specification would normally answer are,
deliberately, left open — see [Open Questions](#open-questions).

## Purpose

`Models` is the SDK's typed data layer: the request, response, and internal data
structures that give every other component in this series something concrete to
exchange. Earlier specifications named this need without defining it —
[SPEC-005](transport.md#response-handling) returns "an SDK-internal response
representation" without specifying its shape, and
[SPEC-007](exceptions.md#universal-logrhythm-error) models LogRhythm's standard
error body as "a separate, structured error object" without defining it either.
`Models` is where those shapes are actually defined.

**Decision: version 1 uses Pydantic v2, exclusively**, for every model in the SDK —
public and internal, request and response. No `dataclasses` are used anywhere in
this architecture. This is a foundational decision that everything else in this
specification builds on — see
[ADR-0005](../adr/0005-pydantic-v2-models.md) for the full decision and its
alternatives.

## Scope

**In scope:**

- Request models, response models, and internal models.
- A small, shared base hierarchy.
- Common properties every model has (immutability, strict typing, validation).
- Manufacturer field aliasing.
- Serialization behavior (Python, API, and JSON representations).
- Validation strictness, separated by model family.
- Enum handling.
- Date/time normalization.
- The universal LogRhythm error body as a model.
- Handling of sensitive fields.
- Partial updates (`unset` vs. `None`).
- Model organization and the public import surface.

**Out of scope** (defined by
[SPEC-009 — Filters, Pagination, Sorting and Options](filters-and-options.md), or
referenced only):

- Filters.
- Pagination.
- Query builders.
- Options.
- Concrete Python implementation.
- Concrete API endpoints.

## Responsibilities

`Models`:

- represents every request, response, and internal data structure in the SDK as a
  typed, validated Pydantic model (see [Base Models](#base-models)).
- enforces strict validation on outgoing data and appropriately tolerant validation
  on incoming data (see [Request Models](#request-models) and
  [Response Models](#response-models)).
- maps manufacturer field names to SDK field names explicitly (see
  [Aliases](#aliases)).
- normalizes date/time values to a single internal representation (see
  [Date and Time](#date-and-time)).
- keeps sensitive fields from leaking through default representations (see
  [Sensitive Fields](#sensitive-fields)).
- distinguishes an unset field from an explicit `None` (see
  [Partial Updates](#partial-updates)).
- is organized so that models live close to the resource they describe, and are
  exported from stable, predictable namespaces (see
  [Model Organisation](#model-organisation) and [Public API](#public-api)).
- is testable without real network access or real secrets (see
  [Testability](#testability)).

## Non-Responsibilities

`Models`:

- does not perform HTTP requests or transport-level work — see
  [SPEC-005](transport.md#purpose).
- does not build filters, queries, or pagination logic — see
  [SPEC-009](filters-and-options.md#purpose).
- does not know about concrete API endpoints.
- does not decide what gets logged — see [SPEC-006](logging.md#purpose).
- does not raise or define exceptions itself — model validation failures surface
  as [SPEC-007](exceptions.md#model-errors)'s `ModelError` family, not as
  something `Models` defines independently.

## Model Families

Every model belongs to one of three families, distinguished by what they represent
and how strictly they are validated:

- **Request models** — data the SDK sends to LogRhythm. See
  [Request Models](#request-models).
- **Response models** — data LogRhythm sends back. See
  [Response Models](#response-models).
- **Internal models** — data structures used by `core` infrastructure
  ([Transport](transport.md), [Logging](logging.md), [Exceptions](exceptions.md))
  that are not necessarily part of any LogRhythm request or response at all. See
  [Internal Models](#internal-models).

These families exist because a request and a response have fundamentally different
validation needs (see [Request Models](#request-models) vs.
[Response Models](#response-models)) — not because of an arbitrary taxonomy.

## Base Models

**Decision: the base hierarchy stays deliberately small.** Conceptually:

```text
BaseModel
    ↓
SdkModel
    ↓
    ├── RequestModel
    ├── ResponseModel
    └── InternalModel
```

`SdkModel` carries whatever behavior is genuinely common to every model in the SDK.
Further base classes are added **only** where there is real, shared behavior to
justify them — not speculatively. This is a direct application of
[SPEC-000](design-principles.md#architecture-principles)'s "Composition over
inheritance" and "No speculative abstractions" principles, already used the same
way for `TransportProtocol` in [SPEC-005](transport.md#transport-model).

**All models share the following properties, without exception:**

- **immutable / frozen** — see [Immutability](#immutability).
- **keyword-only** construction — no positional arguments.
- **fully typed** — every field has an explicit type.
- **validated** — no model exists in a partially valid state (consistent with
  [SPEC-002](configuration.md#validation)'s "no partially valid" principle, applied
  here to models instead of `Configuration`).
- **documented** — every public model and field is documented, per
  [SPEC-000](design-principles.md#implementation-principles)'s Google-style
  docstring requirement.

No Python class definitions, method signatures, or attributes are given here —
consistent with every other specification in this series.

## Request Models

Request models represent data the SDK is about to send. Bindingly:

- **Validate strictly.**
- **Reject unknown fields** — a request model does not silently accept a field it
  does not recognize.
- **Use explicit manufacturer aliases** (see [Aliases](#aliases)).
- **Serialize using manufacturer field names only** — never the SDK's internal
  Python field names (see [Serialization](#serialization)).
- **Do not send unset fields by default** — see [Partial Updates](#partial-updates).
- **Distinguish `unset` from `None`** — see [Partial Updates](#partial-updates).
- **No automatic type coercion.** A caller supplying the wrong type gets a
  validation failure, not a silent conversion.

**Create, Update, Delete, and Upsert:**

- **Create and Update models are, in general, separate models** — even where their
  fields overlap, they represent different operations with different validation
  needs (e.g. a Create model may require a field an Update model treats as
  optional).
- **`Upsert` may only be used where the underlying API genuinely has upsert
  semantics** — it is not a convenience alias for "create or update" invented by
  the SDK.
- **A Delete operation gets its own model only if the API defines a structured
  request body for it.** A bodyless delete does not get a model just for the sake
  of consistency.

## Response Models

Response models represent data LogRhythm returns. Bindingly:

- **Validate known fields.**
- **Allow unknown fields** — an undocumented or newly added field from the server
  does not fail validation.
- **Retain unknown fields** — they are not silently discarded; see
  [Public API](#public-api) regarding their stability.
- **Use manufacturer aliases** (see [Aliases](#aliases)), the same as request
  models.
- **Normalize only specific, documented special cases** — never a general, loose
  type-coercion policy. Response models are tolerant of *shape* (unknown fields)
  but not casually tolerant of *type*.

This asymmetry — strict on the way out, tolerant (but not loose) on the way in — is
deliberate: outgoing data is entirely under the SDK's control and should be
correct by construction, while incoming data comes from a system the SDK does not
control and must not break on fields it does not yet know about.

## Internal Models

**Decision: internal models also use Pydantic** — there is no separate, lighter
mechanism for `core` infrastructure. Illustrative examples (not an exhaustive or
final list):

- `RequestContext` (see [SPEC-006, Request Context](logging.md#request-context))
- `TransportResponse` — the SDK-internal response representation
  [SPEC-005](transport.md#response-handling) already describes conceptually,
  without naming it
- Transport metadata (see
  [SPEC-005, Logging Metadata](transport.md#logging-metadata) and
  [Debug Metadata](transport.md#debug-metadata))
- Logging events (see [SPEC-006, Structured Events](logging.md#structured-events))
- Safe response snippets (see
  [SPEC-007, Response Snippets](exceptions.md#response-snippets))
- The universal LogRhythm error object (see
  [Universal LogRhythm Error Model](#universal-logrhythm-error-model))

**Internal models are not automatically part of the public API.** Being a Pydantic
model does not, by itself, make something publicly exported — see
[Public API](#public-api).

## Validation

- **Request models validate strictly**, with no automatic type coercion (see
  [Request Models](#request-models)).
- **Response models validate strictly for known fields**, per documented shape, with
  normalization limited to specific, documented special cases (see
  [Response Models](#response-models)).
- **Presence, nullability, and type are tracked independently for every field.** A
  field being required or optional (presence), a field being allowed to be `None`
  (nullability), and a field's type are three separate, deliberately distinguished
  properties — none is inferred from another.
- A validation failure surfaces as [SPEC-007](exceptions.md#model-errors)'s
  `RequestValidationError` or `ResponseValidationError`, depending on which side of
  the request/response boundary it occurred on — `Models` does not define a
  competing error mechanism of its own.

## Immutability

**Decision: every model is immutable.** A model is never mutated after creation;
changing a model's data always produces a **new** object.

Suitable factory or helper methods may be provided for this purpose — for example,
something like `from_existing(...)` or `with_changes(...)`. **The concrete API for
this is not decided by this specification** — see [Open Questions](#open-questions).

## Aliases

**Decision: every manufacturer field name is defined through an explicit Pydantic
alias** — never inferred or generated automatically. Examples:

- `statusCode` → `status_code`
- `upstreamError` → `upstream_error`

**No global, blanket alias-generation mechanism (e.g. a universal
camelCase-to-snake_case transform) is used.** Each alias is deliberate and
reviewable, consistent with
[SPEC-000](design-principles.md#implementation-principles)'s "No hidden magic"
principle — an automatic, blanket transform would make the actual wire field name
non-obvious from reading the model.

## Serialization

Models conceptually distinguish three representations:

- **Python representation** — the model as used within SDK/application code
  (SDK-internal field names).
- **API representation** — what is actually sent to or received from LogRhythm
  (manufacturer field names; see [Aliases](#aliases)).
- **JSON representation** — the serialized wire form of the API representation.

**Requests are serialized using manufacturer aliases** — never the SDK's internal
field names (see [Request Models](#request-models)).

## Enums

**Decision: version 1 uses only typed enums**, expected to be `StrEnum` and/or
`IntEnum`. **Enums are strict in both directions** — constructing an enum from an
unknown value, and encountering an unknown value while validating incoming data,
both produce a validation failure rather than silently passing an unrecognized
value through.

## Date and Time

**Decision: every date/time value is represented internally as a timezone-aware
UTC `datetime`.**

- **Naive datetimes are always rejected** — a value with no timezone information is
  never accepted as-is.
- **On input, values are normalized to UTC.**
- **The original offset is not retained** once normalized — only the UTC instant
  is kept.
- **On output, each API endpoint's expected format is used for serialization** —
  the internal UTC representation does not imply a single fixed wire format across
  every endpoint.

## Universal LogRhythm Error Model

[SPEC-007](exceptions.md#universal-logrhythm-error) already establishes that
LogRhythm's standardized error body is modeled as a separate, structured object,
held optionally by `ApiError`. This specification defines how that object is
modeled:

- **It is an ordinary response model** — the same rules as
  [Response Models](#response-models) apply: known fields validated, unknown
  fields allowed and retained.
- **It uses manufacturer aliases** (see [Aliases](#aliases)), the same as any other
  response model.
- **It is immutable** (see [Immutability](#immutability)), the same as any other
  model.
- **Unknown additional fields are retained**, not discarded — consistent with
  [Response Models](#response-models)' general tolerance policy.

## Sensitive Fields

Models that hold sensitive information — for example a bearer token (see
[SPEC-003](authentication.md#secret-handling)), error details, or other
credentials — **must have safe `repr()` behavior.** Secrets must never be rendered
unfiltered through a model's default string or debug representation.

This is not a new rule: it restates, for models specifically, the same requirement
[SPEC-003](authentication.md#secret-handling),
[SPEC-005](transport.md#redaction), [SPEC-006](logging.md#redaction), and
[SPEC-007](exceptions.md#redaction) already establish for their respective
domains — `Models` introduces no separate or independent secret-handling policy of
its own.

## Partial Updates

**Decision: models must be able to distinguish an unset field from a field
explicitly set to `None`.** This is a required part of the architecture, not an
optional nicety — without it, an Update model cannot correctly express "leave this
field alone" versus "clear this field," which are different operations against the
API.

## Model Organisation

- **Global/shared internal models live under `core/models`** — see
  [Internal Models](#internal-models).
- **Resource models live under `<api>/<resource>/models`** — for example,
  `admin/hosts/models` and `admin/log_sources/models`.
- **No large collection files.** Models are not gathered into one sweeping
  `models.py` per API area; they are organized per resource instead.

**Consistency note:** [Architecture Overview](../architecture/overview.md)'s
existing package-shape diagram previously showed a single `models.py` per API
module (`<api_module>/models.py`), predating this decision. Because leaving that
diagram unchanged would visibly contradict this specification, it has been updated
in this same change to show `models` nested under `<api_module>/<resource>/`
instead — a minimal, necessary consistency fix, not a new decision beyond what is
stated here. The placement of `filters.py`, `resources.py`, and `client.py` is
unaffected and not addressed by this specification — filters belong to
[SPEC-009](filters-and-options.md).

## Public API

**Decision: models are exported from stable namespaces** — for example,
`logrhythm_sdk.admin.hosts.models` — **not from deep internal files.** A caller
importing a model does so from the resource-level namespace, not from whatever
internal module happens to define it.

**JSON Schema:** Pydantic generates JSON Schema for every model. **This currently
serves documentation and tooling purposes only — it is not a stable public
contract.** A caller must not depend on the exact shape of generated JSON Schema
remaining unchanged across releases.

## Failure Behaviour

Model construction and validation follow Fail Fast, per
[SPEC-000](design-principles.md#implementation-principles): an invalid model is
never partially constructed or silently accepted — validation either succeeds
completely or fails immediately, surfacing as the appropriate
[SPEC-007](exceptions.md#model-errors) exception. `Models` does not introduce any
exception to Fail Fast the way [SPEC-006](logging.md#failure-behaviour) does for
logging — there is no category of model failure that is allowed to pass silently.

## Testability

- `Models` must be fully testable without real network access, consistent with
  [SPEC-000](design-principles.md#testability).
- Tests can construct any model directly, with placeholder data.
- Alias mapping (see [Aliases](#aliases)) must be testable in both directions:
  constructing from manufacturer field names, and serializing back to them.
- Date/time normalization (see [Date and Time](#date-and-time)) must be
  deterministic and testable without relying on the system's local timezone.
- Safe `repr()` behavior for sensitive fields (see
  [Sensitive Fields](#sensitive-fields)) must be independently verifiable by a
  test, consistent with [SPEC-005](transport.md#testability) and
  [SPEC-006](logging.md#testability)'s equivalent requirements for redaction.
- No real secrets, credentials, or production response data are used in this
  specification or in any test; placeholders only.

## Examples

Pseudocode only — illustrative of intended usage, not a committed API surface, not
a real implementation, and not a claim about any concrete field name or class
signature. Placeholder values only; no real secrets or response data.

**Conceptual shape of a request/response model pair (illustrative only, not a
class):**

```text
# Request model: strict, rejects unknown fields, sends manufacturer aliases only
CreateHostRequest:
    name: str
    entity_id: int          # alias: entityId

# Response model: tolerant of unknown fields, retains them
Host:
    id: int
    name: str
    status_code: int        # alias: statusCode
    # ...unknown fields from the server are retained, not dropped
```

**Importing from a stable, resource-level namespace:**

```python
from logrhythm_sdk.admin.hosts.models import Host, CreateHostRequest
```

**Conceptual immutable update (illustrative only — exact API not decided):**

```python
updated_host = existing_host.with_changes(name="new-name")
# `existing_host` is unchanged; `updated_host` is a new, distinct object
```

## Open Questions

These are explicitly undecided. They must not be resolved silently by
implementation; each requires an explicit decision (and, where architecturally
significant, an ADR) before it can move out of this list.

- **Concrete factory/update methods.** The exact API for producing a modified copy
  of an immutable model (see [Immutability](#immutability)) — for example, whether
  it is named `with_changes(...)`, something else, or follows a different pattern
  entirely.
- **Final `SdkModel` configuration.** The complete, concrete Pydantic
  configuration shared by every model, beyond the properties already decided in
  [Base Models](#base-models).
- **Field-specific special-case normalization.** Which individual response fields
  receive documented special-case normalization (see
  [Response Models](#response-models)), and what that normalization does, on a
  field-by-field basis.
- **Bulk endpoint modeling.** How request/response models will represent future
  bulk operations, once such endpoints are actually inventoried.

## Future Extensions

These are possible ideas for later, explicitly non-binding, and do not represent
any architectural decision or part of SPEC-008:

- Automatic model migration.
- Code generation.
- Schema versioning.
- OpenAPI generation.
- Performance optimizations.

## Non-Goals

This specification, and by extension `Models` itself, explicitly does not cover:

- Filters, pagination, query builders, or options — see
  [SPEC-009 — Filters, Pagination, Sorting and Options](filters-and-options.md).
- HTTP or transport implementation.
- Logging implementation.
- The exception hierarchy itself (only where models participate in it — see
  [SPEC-007](exceptions.md#model-errors)).
- Concrete API endpoints.
- Concrete Python implementation.

## References

- [SPEC-000 — Design Principles](design-principles.md)
- [SPEC-001 — SDK Client](sdk-client.md)
- [SPEC-002 — Configuration](configuration.md)
- [SPEC-003 — Authentication](authentication.md)
- [SPEC-005 — Transport](transport.md)
- [SPEC-006 — Logging](logging.md)
- [SPEC-007 — Exception Handling](exceptions.md)
- [Architecture Overview](../architecture/overview.md)
- [Component Model](../architecture/components.md)
- [ADR-0005 — Use Pydantic v2 for SDK models](../adr/0005-pydantic-v2-models.md) —
  the Pydantic decision [Purpose](#purpose) and [Base Models](#base-models) rely
  on.
