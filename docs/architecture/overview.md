# Architecture Overview

> **Status of this document:** this describes the **target architecture** for the SDK.
> Almost none of it is implemented yet. This foundation phase only ships the package
> skeleton (`logrhythm_sdk` and `logrhythm_sdk.core`, both currently empty of logic).
> Sections below are written in the future tense on purpose; nothing here should be
> read as "already available."

## Goals of this document

Describe the intended shape of the SDK so that later implementation phases build
toward a consistent target, rather than each API module inventing its own structure.
For a component-level diagram of this same target, see
[Component Model](components.md). For the concrete architecture and implementation
rules that follow from this shape, see
[Design Principles](../specifications/design-principles.md).

## High-level shape

```text
logrhythm_sdk/
├── __init__.py          Public, high-level facade (e.g. a future LogRhythmClient)
├── core/                 Shared infrastructure used by every API module
│   └── models/            Shared/internal SDK-wide models (see SPEC-008)
└── <api_module>/         One package per LogRhythm API area (added when implemented)
    ├── client.py           Thin client grouping that API area's resources
    └── <resource>/         One subpackage per resource within that API area
        ├── resource.py       Endpoint methods for that resource
        ├── models/            Typed data structures for that resource (see SPEC-008)
        ├── filters/            Filter models for that resource (see SPEC-009)
        ├── sorting/             Sorting models for that resource (see SPEC-009)
        └── options/              Functional options for that resource (see SPEC-009)
```

This nesting is resource-first, not file-type-first: models, filters, sorting, and
options each live inside the resource subpackage they belong to, rather than in one
collection file per API module. Model placement follows
[SPEC-008 — Models](../specifications/models.md#model-organisation); filters,
sorting, and options follow
[SPEC-009](../specifications/filters-and-options.md#model-organisation); the
`client.py` / `resource.py` split follows
[SPEC-010 — Client Hierarchy](../specifications/api-modules.md#client-hierarchy)
and [Resource Hierarchy](../specifications/api-modules.md#resource-hierarchy).

### Central high-level facade

A single high-level entry point (planned as `LogRhythmClient`, not yet implemented)
will expose the supported API areas as attributes (for example, a future
`client.search` or `client.alarms`). It is a thin composition layer: it wires together
shared transport/configuration from `core` and the individual API clients. It does not
contain API-specific logic itself.

### `core`: shared infrastructure

`logrhythm_sdk.core` is the only place shared, cross-API logic is allowed to live.
Planned responsibilities (none implemented yet):

- **Transport** — the underlying HTTP client used by all API modules.
- **Configuration** — loading and validating connection settings.
- **Authentication** — attaching bearer tokens to outgoing requests.
- **TLS handling** — certificate verification behavior.
- **Logging** — structured, secret-redacting logging.

API modules depend on `core`; `core` never depends on a specific API module.

### API modules

The SDK supports seven LogRhythm API areas, in this implementation order —
Administration, AI Engine Cache Drilldown, Metrics, AI Engine, Alarm, Case, and
Search (see
[SPEC-010 — Supported APIs](../specifications/api-modules.md#supported-apis)).

Each becomes its own package with the same internal shape (see
[High-level shape](#high-level-shape) above):

- **API client** (`client.py`) — groups that API area's resources; binds `core`
  transport/configuration to them.
- **Resource** (`resource.py`) — resource-oriented endpoint methods, one
  subpackage per resource.
- **Models** — typed representations of the resources that resource returns or
  accepts.
- **Filters, sorting, options** — typed helpers for that resource's query
  parameters (see [SPEC-009](../specifications/filters-and-options.md)).

Keeping this structure identical across API modules — and across resources within
an API module — is a deliberate choice: once a developer understands one resource,
they understand the shape of all of them.

### Separation of concerns

- **Transport** (how requests are sent) is decided in `core` and is never
  reimplemented per API module.
- **Configuration** (where settings come from) is decided in `core`.
- **API-specific logic** (endpoints, request/response shapes, resource semantics)
  lives exclusively inside that API's own module.

## Planned configuration

Configuration will be loadable from YAML, JSON, or TOML sources (not implemented in
this phase). Planned configuration concerns:

- **Authentication** — bearer token authentication.
- **Connection settings** — one HTTPS base host and global port for all API modules,
  plus shared timeout settings. Per-API hosts and ports are not part of version 1.
- **API paths** — each API module ships static, sensible default paths, with optional
  overrides for non-standard deployments.
- **TLS** — three supported modes: verification against the system trust store,
  verification against a custom CA bundle, and explicit, deliberate opt-out of
  verification (never the default).

## Planned logging

File-based logging will support both plain text and JSON output. All logging is
expected to pass through secret-redaction so that bearer tokens and other credentials
are never written to log output, regardless of log level or format.

## Synchronous first

The initial public API surface will be synchronous. Asynchronous support is a
possible future extension, not a goal for the initial implementation phases, and will
only be pursued if it does not compromise the clarity of the synchronous API.
