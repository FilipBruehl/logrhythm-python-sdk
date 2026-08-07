# SPEC-NNN — \<Component Name\>

<!--
  Template only — not a real specification. This shape matches SPEC-001
  through SPEC-010; SPEC-000 (Design Principles) is a deliberate exception
  and does not follow this template. See docs/specifications/README.md for
  the binding numbering, status model, change process, and Review Criteria
  this template does not repeat. If anything here conflicts with
  docs/specifications/README.md, that document wins — see
  docs/development/templates.md#template-governance.

  Copy this file to docs/specifications/<short-slug>.md, replace SPEC-NNN
  with the next sequential ID (see docs/specifications/README.md's index),
  and add a row there once the file exists.
-->

| Field | Value |
| --- | --- |
| ID | SPEC-NNN |
| Status | Draft |
| Phase | \<phase identifier\> |
| Component | \<Component Name\> |
| Depends on | SPEC-000 (`design-principles.md`)\<, other SPECs this one builds on\> |
| Implementation | Not implemented |

## Status

<!-- State plainly that this is Draft, not yet reviewed against the Review
     Criteria, and not binding — matching every other Draft spec's opening
     paragraph. Note here if specific questions are deliberately left open. -->

## Purpose

<!-- What this component is, in a few sentences, and why it needs its own
     specification rather than being folded into another one. -->

## Scope

**In scope:**

<!-- What this specification decides. -->

**Out of scope** (referenced only; defined by their own specifications):

<!-- What is deliberately left to other, existing or future specifications. -->

## Responsibilities

<!-- What this component does, as a list of concrete responsibilities. -->

## Non-Responsibilities

<!-- What this component explicitly does not do — the mirror of
     Responsibilities, stated to prevent scope creep during implementation. -->

## Decisions

<!--
  In practice, this is usually several specifically-named sections rather
  than one generic "Decisions" heading — see how SPEC-005 has "Transport
  Model", "URL Resolution", "HTTP Client Management", etc. Replace this
  placeholder with as many named sections as the component actually needs,
  each stating its decision(s) explicitly (bold "Decision: ..." lead-ins are
  the established style — see any existing SPEC-00N for examples).
-->

## Failure Behaviour

<!-- How this component fails — categories of error it can produce or
     surface, and whether Fail Fast (SPEC-000) applies without exception. -->

## Testability

<!-- What must be true for this component to be tested without real network
     access, per SPEC-000's Testability principles. -->

## Examples

<!-- Pseudocode only — illustrative of intended usage, not a committed API
     surface, not a real implementation. Placeholder values only; no real
     credentials or hosts. -->

## Open Questions

<!-- Explicitly undecided items. Each must be resolved by an explicit
     decision (and, where architecturally significant, an ADR) before it can
     move out of this list — never resolved silently by implementation. -->

## Future Extensions

<!-- Possible ideas for later, explicitly non-binding, not part of this
     specification's decisions. -->

## Non-Goals

<!-- What this specification, and the component it describes, deliberately
     does not cover — distinct from Non-Responsibilities above, which is
     about behavior; this is about scope of the document itself. -->

## References

<!-- SPEC-000, any SPECs this one depends on, Architecture Overview,
     Component Model, and any ADR this specification's decisions rely on.
     If no ADR applies, say so explicitly (see existing SPECs' References
     sections for the established phrasing). -->

## Review Criteria

<!--
  Self-check before proposing this specification for review — see
  docs/specifications/README.md#review-criteria for what each item means.
  This is a checklist, not a restatement of the criteria themselves.
-->

- [ ] Scope is fully defined (in scope and out of scope)
- [ ] Responsibilities are clearly described
- [ ] The public interface is documented
- [ ] Non-goals are documented
- [ ] Security aspects are addressed, where relevant
- [ ] A test strategy is described
- [ ] Open questions are clearly marked
- [ ] No contradictions with existing ADRs
- [ ] No contradictions with SPEC-000 — Design Principles
      (`docs/specifications/design-principles.md`)
