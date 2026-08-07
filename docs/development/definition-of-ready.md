# Definition of Ready

An implementation task may begin only once every item below holds. If any item
is unmet, the task is not ready: the correct response is to close the gap (or
raise the question, per
[`AGENTS.md`](../../AGENTS.md#architecture-governance)) before
writing any code — never to proceed on an assumption.

## SPEC status

- A relevant Design Specification exists under `docs/specifications/` and is at
  `Accepted` status (see
  [Design Specifications, Status model](../specifications/README.md#status-model)).
  Per that status model, no implementation may start from a `Draft` or
  `In Review` specification.
- If no SPEC covers the area at all, one is written and reaches `Accepted`
  first — that is architecture work, not implementation work, per
  [SPEC-000](../specifications/design-principles.md#documentation-principles)'s
  "Architecture before implementation" principle.

## ADR status

- Any ADR the task depends on (e.g. a core library choice, a security-relevant
  decision) already exists and is `Accepted` — or the task genuinely requires
  no new architectural decision. See
  [ADR Policy](../adr/README.md#when-an-adr-is-required) for when a new ADR
  must exist before proceeding.

## Open architecture questions

- No unresolved Open Question in the relevant SPEC(s) blocks the task's scope.
  If one does, it is resolved explicitly — a decision, and where warranted a
  new ADR — before implementation starts, never silently assumed away. See
  [Architecture Governance](../../AGENTS.md#architecture-governance).

## Vendor / API documentation

- For work implementing a LogRhythm endpoint: the official LogRhythm
  documentation for the target endpoint(s) has already been captured and
  extracted per [API Implementation Workflow](api-implementation-workflow.md)
  steps 1–2 (documentation page identified; facts, schemas, parameters, and
  uncertainties written down). Implementation never starts from memory or
  assumption about vendor behavior — see
  [`AGENTS.md`](../../AGENTS.md#working-agreements).
- Any documentation gap or ambiguity discovered during that extraction is
  written down explicitly, not resolved by guessing.

## Scope

- The task's scope is stated clearly: which resource/component/document is
  affected, which files are expected to change, and what is explicitly out of
  scope.
- The scope maps cleanly onto one branch per
  [Branch Strategy](branching.md#branch-strategy) (a `feature/*`/`fix/*`
  branch, optionally under an `integration/*` branch). A task whose scope
  doesn't fit one branch cleanly is split before work starts.

## Not required to start

The following are **not** prerequisites, to avoid over-gating small work:

- A pre-existing, separate test plan document — tests are written as part of
  the work itself, per
  [Testing Rules](testing.md#testing-rules-by-change-type).
- Full API Coverage Matrix population for the whole API area — only the
  specific endpoint(s) in scope need their documentation captured.

## See also

- [Definition of Done](definition-of-done.md)
- [Architecture Governance](../../AGENTS.md#architecture-governance)
- [ADR Policy](../adr/README.md#when-an-adr-is-required)
