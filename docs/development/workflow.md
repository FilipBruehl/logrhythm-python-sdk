# Developer Workflow

This page is the entry point to the project's binding development workflow. It
ties together branching, commits, pull requests, readiness/completion
criteria, testing rules, and governance — each documented in its own page so
that process (this page and its links), the practical
[Contribution Guide](contributing.md), and the
[Definition of Done](definition-of-done.md) stay clearly separated.

This workflow is the binding basis for every following development phase,
per [CLAUDE.md](../../CLAUDE.md). It reflects the project's existing
architecture ([SPEC-000 through SPEC-010](../specifications/README.md)),
existing [ADRs](../adr/README.md), and the repository structure and working
style already established in Phases A.1–A.2.

## Where to start

- **New to the repository?** Start with
  [Contributing](contributing.md) for local setup and the required quality
  commands.
- **About to start implementation work?** Check
  [Definition of Ready](definition-of-ready.md) first.
- **About to open a branch?** See
  [Branch Types & Branch Strategy](branching.md).
- **About to commit?** See [Commit Strategy](commits.md).
- **About to open a PR?** See [Pull Requests](pull-requests.md).
- **Wrapping up a change?** Check it against
  [Definition of Done](definition-of-done.md).
- **Writing tests?** See [Testing](testing.md), including
  [Testing rules by change type](testing.md#testing-rules-by-change-type).
- **Working with (or as) Claude Code?** See
  [Claude Workflow & Architecture Governance](claude-workflow.md).
- **Wondering whether a decision needs an ADR?** See
  [ADR Policy](../adr/README.md#when-an-adr-is-required).
- **Implementing a LogRhythm API endpoint?** See
  [API Implementation Workflow](api-implementation-workflow.md).

## Workflow documents

| Document | Covers |
|---|---|
| [Branch Types & Branch Strategy](branching.md) | `main`, `integration/*`, `feature/*`, `fix/*`; creation, updates, merge order, lifecycle, deletion. |
| [Commit Strategy](commits.md) | Conventional Commits, allowed types, scopes, commit size/content, linear history. |
| [Pull Requests](pull-requests.md) | When a PR is required, required content, Definition of Review, merge prerequisites, Branch Protection (conceptual). |
| [Definition of Ready](definition-of-ready.md) | When an implementation task may begin. |
| [Definition of Done](definition-of-done.md) | When a work package is complete. |
| [Testing](testing.md) | Test suite layout, coverage target, and rules by change type. |
| [Claude Workflow & Architecture Governance](claude-workflow.md) | Architecture Governance (Claude never decides architecture alone), Claude's branch/commit/push/PR permissions, Git Safety Rules. |
| [ADR Policy](../adr/README.md#when-an-adr-is-required) | When a new ADR is required, and when it isn't. |
| [Dependencies & Tooling](dependencies.md) | Runtime dependency baseline, dependency placement/versioning, and the upgrade process. |
| [Contributing](contributing.md) | Local setup and required quality commands. |
| [API Implementation Workflow](api-implementation-workflow.md) | The process for implementing a new LogRhythm API area. |

## What this phase does not cover

Per its own scope, this documentation phase does not introduce pre-commit
hooks, GitHub Actions, PR/issue templates, Claude Code settings, runtime
dependencies, runtime code, or runtime configuration. The rules above are,
for now, applied manually and reviewed by hand; automated enforcement is a
later phase.
