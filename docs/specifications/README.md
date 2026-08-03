# Design Specifications

This directory holds Design Specifications: the documents that describe **how** a
component of the SDK is built, once an underlying architectural direction has already
been decided.

## Purpose

A Design Specification takes an accepted decision and turns it into a concrete,
implementable design: which module it lives in, what its public shape looks like,
how it composes with `core` and other components, and what its behavior is for the
cases that matter. Specifications exist so that implementation work has a reviewed
target to build toward, instead of being designed ad hoc while writing code.

[SPEC-000 — Design Principles](design-principles.md) is the one specification that
applies project-wide rather than to a single component; every other specification is
expected to follow it.

## Numbering

Every specification is assigned a stable, sequential ID — `SPEC-000`, `SPEC-001`, and
so on — stated in its title (`# SPEC-NNN — <Title>`). The ID is assigned once, in
order of creation, and never reused or renumbered, so it stays a stable way to
reference a specification regardless of later title or filename changes. Current
specifications:

| ID | Title | Status | File |
| --- | --- | --- | --- |
| SPEC-000 | Design Principles | Draft | [design-principles.md](design-principles.md) |
| SPEC-001 | SDK Client | Draft | [sdk-client.md](sdk-client.md) |
| SPEC-002 | Configuration | Draft | [configuration.md](configuration.md) |
| SPEC-003 | Authentication | Draft | [authentication.md](authentication.md) |
| SPEC-004 | TLS | Draft | [tls.md](tls.md) |
| SPEC-005 | Transport | Draft | [transport.md](transport.md) |
| SPEC-006 | Logging | Draft | [logging.md](logging.md) |
| SPEC-007 | Exception Handling | Draft | [exceptions.md](exceptions.md) |
| SPEC-008 | Models | Draft | [models.md](models.md) |
| SPEC-009 | Filters, Pagination, Sorting and Options | Draft | [filters-and-options.md](filters-and-options.md) |
| SPEC-010 | API Modules | Draft | [api-modules.md](api-modules.md) |

## Where this fits

```text
ADR                  →  Why
Design Specification →  How
Code                  →  The actual implementation
User documentation    →  What is actually available today
```

- **ADR** (`docs/adr/`) — records *why* a significant, durable architectural decision
  was made: the context, the decision, and its consequences. See
  [docs/adr/README.md](../adr/README.md).
- **Design Specification** (this directory) — records *how* that decision is realized
  in the SDK's structure: module layout, public shape, composition, and behavior for
  the cases the spec covers.
- **Code** (`src/logrhythm_sdk/`) — the actual implementation, built to match an
  Accepted specification. See
  [API Implementation Workflow](../development/api-implementation-workflow.md) for the
  step-by-step process that goes from an official LogRhythm documentation page to
  implemented, tested code.
- **User documentation** (`README.md`, `/docs` guides) — describes *only* functionality
  that is actually implemented and available today. A specification being written or
  even Accepted does not make its subject "available" in user documentation.

An ADR does not need to restate implementation detail, a specification does not need
to re-argue the decision it implements, and user documentation never gets ahead of
what the code actually does.

## Status model

A specification moves through the following statuses:

| Status | Meaning |
| --- | --- |
| `Draft` | Being written or actively discussed; not yet reviewed as a whole. Implementation must not start from a Draft. |
| `In Review` | Complete and under review by maintainers/contributors. |
| `Accepted` | Reviewed and approved as the target design; meets the [Review Criteria](#review-criteria) below. Implementation may begin or continue against it. |
| `Implemented` | The code matches this specification. Cross-check against [API Coverage Matrix](../coverage/api-coverage.md) where applicable. |
| `Superseded` | Replaced by a newer specification, which is linked from this one. |

## Review Criteria

This is the project-wide review standard for specifications. A specification cannot
be marked `Accepted` until all of the following are satisfied:

- **Scope is fully defined.** What the specification covers — and, just as
  importantly, what it explicitly does not cover — is stated unambiguously.
- **Responsibilities are clearly described.** It is unambiguous which component owns
  which behavior, consistent with [SPEC-000](design-principles.md) (Single
  Responsibility, separation of concerns).
- **The public interface is documented.** Anything a consumer of the SDK will see —
  signatures, types, exceptions raised — is specified, not left to be decided during
  implementation.
- **Non-goals are documented.** What the specification deliberately leaves out is
  stated explicitly, so implementers do not scope-creep beyond what was reviewed.
- **Security aspects are addressed.** Where relevant, the specification states how it
  upholds [SPEC-000's security principles](design-principles.md#security-principles)
  (e.g. secret handling, TLS behavior) rather than leaving them implicit.
- **A test strategy is described.** How the design will be verified — unit tests,
  mocked infrastructure, integration tests where applicable — is part of the
  specification, not an afterthought added during implementation.
- **Open questions are clearly marked.** Anything still undecided or dependent on
  information not yet available (e.g. unclear vendor documentation) is called out
  explicitly, not silently glossed over. See
  [API Implementation Workflow](../development/api-implementation-workflow.md) on not
  inventing behavior to fill such gaps.
- **No contradictions with ADRs.** The specification is consistent with every
  applicable decision in [docs/adr/](../adr/README.md). A specification that needs to
  contradict an ADR must instead propose a new or updated ADR first.
- **No contradictions with the Design Principles.** The specification is consistent
  with [SPEC-000](design-principles.md); a specification that needs an exception to a
  principle states the exception and its reasoning explicitly, rather than silently
  diverging.

A specification missing any of these is not ready for `Accepted` — it stays `Draft`
or `In Review` until the gap is closed.

## Change process

1. Propose the specification (new file) or the change (edit to an existing file) as
   part of a small, reviewable change, per [CLAUDE.md](../../CLAUDE.md). The
   [Specification template](../templates/specification-template.md) is a
   starting-point skeleton for a new file — see
   [Repository Templates](../development/templates.md) — but this page
   remains the normative source for the numbering, status model, and Review
   Criteria it does not repeat.
2. State the status at the top of the file at all times, per the status model above.
3. If a proposed change would contradict or replace an existing ADR's decision, raise
   a new or updated ADR first — a specification implements a decision, it does not
   make one silently. See [CLAUDE.md](../../CLAUDE.md), "Documentation duties".
4. Once implementation reveals that a specification does not match reality (a gap,
   an error, or a necessary adjustment), update the specification in the same change
   that adjusts the code, rather than letting the two drift apart.
5. Mark a specification `Superseded` (with a link to its replacement) instead of
   deleting it, so the history of a design decision stays traceable.

## Bindingness

An `Accepted` (or later) specification is binding for implementation: code that
deviates from it without updating the specification first is a bug in either the code
or the specification. `Draft` and `In Review` specifications are not binding — they
are proposals and may still change substantially before implementation starts.
