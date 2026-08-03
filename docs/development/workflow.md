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
style already established in Phases A.1–A.3.

## Where to start

- **New to the repository?** Start with
  [Contributing](contributing.md) for local setup and the required quality
  commands, then [Pre-Commit](pre-commit.md) to install the local git hooks.
- **About to start implementation work?** Check
  [Definition of Ready](definition-of-ready.md) first.
- **About to open a branch?** See
  [Branch Types & Branch Strategy](branching.md).
- **About to commit?** See [Commit Strategy](commits.md).
- **About to open a PR?** See [Pull Requests](pull-requests.md); it will run
  through `CI / quality` and `CI / test` automatically — see
  [GitHub Actions: CI & Build](ci.md).
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
| [Pull Requests](pull-requests.md) | When a PR is required, required content, Definition of Review, merge prerequisites, Branch Protection recommendations. |
| [Definition of Ready](definition-of-ready.md) | When an implementation task may begin. |
| [Definition of Done](definition-of-done.md) | When a work package is complete. |
| [Testing](testing.md) | Test suite layout, coverage target, and rules by change type. |
| [Claude Workflow & Architecture Governance](claude-workflow.md) | Architecture Governance (Claude never decides architecture alone), Claude's branch/commit/push/PR permissions, Git Safety Rules. |
| [ADR Policy](../adr/README.md#when-an-adr-is-required) | When a new ADR is required, and when it isn't. |
| [Dependencies & Tooling](dependencies.md) | Runtime dependency baseline, dependency placement/versioning, and the upgrade process. |
| [Contributing](contributing.md) | Local setup and required quality commands. |
| [Pre-Commit & Local Code Quality Automation](pre-commit.md) | Local git hooks (pre-commit/pre-push), secret detection, the `uv-lock` hook, and the local quality check (`pre-commit run --all-files`). |
| [GitHub Actions: CI & Build](ci.md) | Server-side `CI / quality` → `CI / test` pipeline, the separate build/package-verification workflow, actionlint, SHA-pinning, and Branch Protection recommendations. |
| [API Implementation Workflow](api-implementation-workflow.md) | The process for implementing a new LogRhythm API area. |

## What is and isn't automated yet

Formatting, linting, type checking, basic file hygiene, secret detection,
lockfile freshness, and workflow linting are enforced both locally (git hooks,
see [Pre-Commit & Local Code Quality Automation](pre-commit.md)) and
server-side (see [GitHub Actions: CI & Build](ci.md)) on every pull request
and relevant push; the full test suite runs before every push locally and as
part of CI; packaging is independently verified by a separate build workflow.
What remains manual, applied by hand rather than enforced by tooling: actual
branch protection settings (documented, not yet configured in GitHub), PR and
issue templates, Claude Code settings, commit-message linting, Markdown
linting, and release/publish automation (planned for Phase A.3.7) — these
remain later steps or phases.
