# Development Roadmap

This roadmap is the central, versioned planning baseline for implementation order.
It does not replace accepted architecture decisions or technical specifications.

## Purpose and boundaries

The repository uses distinct, non-overlapping artifacts:

- **Roadmap**: What gets implemented in which order.
- **Design Specifications**: How a component is designed technically.
- **Architecture Decision Records (ADRs)**: Why significant architecture decisions were made.
- **Development documentation**: Process and governance for development and review.
- **Implementation**: The verified code and tests currently present in the repository.

If a roadmap statement conflicts with accepted ADRs, accepted specifications, or
binding development governance, those normative sources take precedence. Such
conflicts must be surfaced explicitly and resolved by project ownership; this
document does not make architecture decisions.

## Status model and lifecycle

Roadmap entries use this status model:

- `Planned`
- `In Preparation`
- `In Progress`
- `In Review`
- `Completed`
- `Blocked`

Rules:

- A roadmap entry is planning context, not automatic implementation approval.
- Before implementation starts, [Definition of Ready](definition-of-ready.md) must be satisfied.
- Open normative decisions (SPEC/ADR/governance) must be resolved before implementation.
- `Completed` is assigned only after [Definition of Done](definition-of-done.md), explicit acceptance, and integration.
- Status is based on the integrated repository state, not local-only work.
- Changes to the approved implementation order require explicit project-owner approval.

## Phase overview

| Phase | Name | Status | Notes |
| --- | --- | --- | --- |
| A | Developer Infrastructure | Completed | Established repository, process, governance, and specification baseline. |
| B.1 | Core Foundations | In Progress | Foundations B.1.1 to B.1.3 completed and integrated; B.1.4 is the next planned foundation. |

### Phase A — Developer Infrastructure

Phase A is completed.

Based on accepted repository documentation and integrated history, Phase A
covered at least:

- foundational repository and package setup;
- development workflow and quality automation;
- architecture and specification baseline establishment.

Detailed historic sub-phase acceptance details are governed by integrated
documentation and history; this roadmap keeps Phase A at a higher planning level
and does not reconstruct undocumented criteria.

## Phase B.1 — Core Foundations

The following implementation order is approved and fixed:

| ID | Foundation | Status |
| --- | --- | --- |
| B.1.1 | Exception Foundation | Completed |
| B.1.2 | Model Foundation | Completed |
| B.1.3 | Configuration Foundation | Completed |
| B.1.4 | Logging Foundation | Planned |
| B.1.5 | Authentication Foundation | Planned |
| B.1.6 | TLS Foundation | Planned |
| B.1.7 | Transport Foundation | Planned |
| B.1.8 | SDK Client Foundation | Planned |
| B.1.9 | Filter Foundation | Planned |
| B.1.10 | API Module Foundation | Planned |

The approved order does not by itself define hard technical dependencies. Actual
technical dependencies remain governed by accepted specifications and ADRs.

### B.1.1 — Exception Foundation

- **Roadmap ID**: B.1.1
- **Status**: Completed
- **Goal**: Establish the public SDK exception hierarchy baseline.
- **Scope (high-level)**: Shared exception categories and public export surface.
- **Explicit out of scope**: Transport/runtime HTTP mapping integration and logging runtime behavior.
- **Normative references**: [SPEC-007](../specifications/exceptions.md), [SPEC-000](../specifications/design-principles.md)
- **Dependencies**: Foundation-level dependency on accepted design principles.
- **Acceptance criteria (high-level)**:
  - Public exception foundation exists in code.
  - Export boundary is explicit and consistent with specification.
  - No unresolved mismatch between documented foundation scope and integrated implementation.

### B.1.2 — Model Foundation

- **Roadmap ID**: B.1.2
- **Status**: Completed
- **Goal**: Establish shared typed model base classes and validation conventions.
- **Scope (high-level)**: SDK-wide model base hierarchy and common model behavior policies.
- **Explicit out of scope**: Concrete endpoint/resource API models and runtime transport binding.
- **Normative references**: [SPEC-008](../specifications/models.md), [ADR-0005](../adr/0005-pydantic-v2-models.md), [SPEC-000](../specifications/design-principles.md)
- **Dependencies**: Accepted model and architecture decisions.
- **Acceptance criteria (high-level)**:
  - Shared model foundation is implemented and integrated.
  - Foundation behavior aligns with accepted specification constraints.
  - Planned endpoint-specific models remain correctly out of scope.

### B.1.3 — Configuration Foundation

- **Roadmap ID**: B.1.3
- **Status**: Completed
- **Goal**: Provide immutable resolved configuration models and internal config file loading baseline.
- **Scope (high-level)**: Configuration model foundation, validation boundaries, supported file-format loading, and safe exception translation boundaries.
- **Explicit out of scope**: Runtime transport/authentication/TLS/logging implementation and client runtime factory behavior.
- **Normative references**: [SPEC-002](../specifications/configuration.md), [ADR-0007](../adr/0007-configuration-file-formats.md), [ADR-0008](../adr/0008-require-https-for-sdk-managed-endpoints.md), [SPEC-007](../specifications/exceptions.md), [SPEC-008](../specifications/models.md)
- **Dependencies**: Exception foundation and model foundation.
- **Acceptance criteria (high-level)**:
  - Configuration foundation scope is integrated and verifiable in code/tests.
  - Public and internal boundaries remain consistent with accepted specification scope.
  - Runtime components outside foundation scope are not represented as implemented.

### B.1.4 — Logging Foundation (next)

- **Roadmap ID**: B.1.4
- **Status**: Planned
- **Goal**: Provide SDK-internal logging infrastructure baseline per [SPEC-006](../specifications/logging.md) as prerequisite for downstream runtime layers.
- **Scope (high-level)**:
  - Logging infrastructure baseline aligned with SPEC-006.
  - Use already implemented logging configuration.
  - Integrate with existing exception foundation.
  - Provide foundational logging capabilities required by subsequent runtime components.
  - Preserve security/redaction/public-API requirements.
- **Explicit out of scope for this roadmap step definition**:
  - Concrete logger/handler implementation details
  - Event ID catalog
  - Concrete logging interface shape
  - Concrete redaction implementation
  - Runtime log rotation implementation details
  - Logging lifecycle and ownership closure decisions
  - Runtime error-handling detail decisions
  - Technical specification closure changes for SPEC-006
- **Normative references**: [SPEC-006](../specifications/logging.md), [SPEC-002](../specifications/configuration.md), [SPEC-007](../specifications/exceptions.md), [SPEC-000](../specifications/design-principles.md)
- **Dependencies**: B.1.1, B.1.2, B.1.3
- **Acceptance criteria (high-level)**:
  - Scope and readiness are clarified through a dedicated architecture/implementation readiness assessment for SPEC-006.
  - No open technical question is silently decided through implementation.
  - Foundation is implementable without redefining accepted architecture authority boundaries.

### B.1.5 — Authentication Foundation

- **Roadmap ID**: B.1.5
- **Status**: Planned
- **Goal**: Establish SDK authentication foundation.
- **Scope (high-level)**: Foundation-level authentication representation and integration points.
- **Explicit out of scope**: Endpoint/resource-specific API implementation.
- **Normative references**: [SPEC-003](../specifications/authentication.md), [SPEC-000](../specifications/design-principles.md)
- **Dependencies**: B.1.3 and B.1.4 for shared configuration/logging baseline.
- **Acceptance criteria (high-level)**:
  - Foundation scope is implementable from accepted specifications.
  - Public boundaries and security handling remain consistent with accepted norms.

### B.1.6 — TLS Foundation

- **Roadmap ID**: B.1.6
- **Status**: Planned
- **Goal**: Establish TLS policy and integration foundation.
- **Scope (high-level)**: Foundation-level TLS handling interfaces and secure defaults.
- **Explicit out of scope**: Full transport runtime behavior.
- **Normative references**: [SPEC-004](../specifications/tls.md), [ADR-0008](../adr/0008-require-https-for-sdk-managed-endpoints.md), [SPEC-000](../specifications/design-principles.md)
- **Dependencies**: B.1.3 and B.1.4.
- **Acceptance criteria (high-level)**:
  - Secure defaults and opt-in semantics remain aligned to accepted decisions.
  - Foundation boundaries are explicit and testable.

### B.1.7 — Transport Foundation

- **Roadmap ID**: B.1.7
- **Status**: Planned
- **Goal**: Establish shared HTTP transport foundation.
- **Scope (high-level)**: Foundation transport boundary and cross-cutting integration points.
- **Explicit out of scope**: Full API module feature implementation.
- **Normative references**: [SPEC-005](../specifications/transport.md), [ADR-0006](../adr/0006-httpx-transport.md), [SPEC-000](../specifications/design-principles.md)
- **Dependencies**: B.1.5 and B.1.6.
- **Acceptance criteria (high-level)**:
  - Shared transport foundation is aligned with accepted architecture boundaries.
  - Error and security integration expectations are reflected at foundation level.

### B.1.8 — SDK Client Foundation

- **Roadmap ID**: B.1.8
- **Status**: Planned
- **Goal**: Establish the high-level SDK client composition root foundation.
- **Scope (high-level)**: Composition root and foundation-level lifecycle/ownership boundaries.
- **Explicit out of scope**: Concrete endpoint-level implementation.
- **Normative references**: [SPEC-001](../specifications/sdk-client.md), [SPEC-010](../specifications/api-modules.md), [SPEC-000](../specifications/design-principles.md)
- **Dependencies**: B.1.5, B.1.6, B.1.7.
- **Acceptance criteria (high-level)**:
  - Foundation composition boundaries are explicit and specification-conformant.
  - Lifecycle/ownership behavior remains inside accepted architecture constraints.

### B.1.9 — Filter Foundation

- **Roadmap ID**: B.1.9
- **Status**: Planned
- **Goal**: Establish shared filter/pagination/sorting/options model foundation.
- **Scope (high-level)**: Foundational query helper model layer.
- **Explicit out of scope**: Resource-specific query semantics beyond foundation.
- **Normative references**: [SPEC-009](../specifications/filters-and-options.md), [SPEC-008](../specifications/models.md), [SPEC-000](../specifications/design-principles.md)
- **Dependencies**: B.1.2 and B.1.7.
- **Acceptance criteria (high-level)**:
  - Foundation behavior is clear and reusable for later API modules.
  - No unsupported endpoint behavior is presented as implemented.

### B.1.10 — API Module Foundation

- **Roadmap ID**: B.1.10
- **Status**: Planned
- **Goal**: Establish the common API module structure foundation.
- **Scope (high-level)**: API module/client/resource structural baseline.
- **Explicit out of scope**: Full endpoint inventory and complete endpoint implementations.
- **Normative references**: [SPEC-010](../specifications/api-modules.md), [SPEC-001](../specifications/sdk-client.md), [SPEC-000](../specifications/design-principles.md)
- **Dependencies**: B.1.7, B.1.8, B.1.9.
- **Acceptance criteria (high-level)**:
  - Foundation structure is aligned with accepted module architecture.
  - Subsequent endpoint work can build on a stable, documented baseline.

## Post-B.1 planning

No additional accepted, binding development phase plan beyond B.1 is currently
documented in repository governance/specification artifacts. Further phases
remain future planning and require explicit documentation and approval before
becoming binding roadmap scope.
