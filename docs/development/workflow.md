# Developer Workflow

This page is the entry point to the project's binding development workflow. It
ties together branching, commits, pull requests, readiness/completion
criteria, testing, releases, and governance — each documented in its own page so
that process (this page and its links), the practical
[Contribution Guide](contributing.md), and the
[Definition of Done](definition-of-done.md) stay clearly separated.

This workflow reflects the project's existing
architecture ([SPEC-000 through SPEC-010](../specifications/README.md)),
existing [ADRs](../adr/README.md), and the repository structure and working
style already established in Phases A.1–A.3. For AI-assisted work,
[`AGENTS.md`](../../AGENTS.md) is the single source of truth for AI Development
governance; this page is a contributor-oriented navigation and automation
summary.

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
  [GitHub Actions: CI, Build & Release](ci.md).
- **Wrapping up a change?** Check it against
  [Definition of Done](definition-of-done.md).
- **Writing tests?** See [Testing](testing.md), including
  [Testing rules by change type](testing.md#testing-rules-by-change-type).
- **Preparing a version or release?** Follow
  [Release & Publishing](release.md) from the dedicated release branch through
  installation verification.
- **Working with an AI Coding Agent?** Start with
  [`AGENTS.md`](../../AGENTS.md). If a tool-specific adapter exists, read it
  after AGENTS.md.
- **Wondering whether a decision needs an ADR?** See
  [ADR Policy](../adr/README.md#when-an-adr-is-required).
- **Implementing a LogRhythm API endpoint?** See
  [API Implementation Workflow](api-implementation-workflow.md).

## Workflow documents

| Document | Covers |
| --- | --- |
| [Branch Types & Branch Strategy](branching.md) | `main`, `integration/*`, `feature/*`, `fix/*`; creation, updates, merge order, lifecycle, deletion. |
| [Commit Strategy](commits.md) | Conventional Commits, allowed types, scopes, commit size/content, linear history. |
| [Pull Requests](pull-requests.md) | When a PR is required, required content, Definition of Review, merge prerequisites, Branch Protection recommendations. |
| [Definition of Ready](definition-of-ready.md) | When an implementation task may begin. |
| [Definition of Done](definition-of-done.md) | When a work package is complete. |
| [Testing](testing.md) | Test suite layout, coverage target, and rules by change type. |
| [Release & Publishing](release.md) | Versioning, changelog, release PR, Trusted Publishing, GitHub Environments, release pipeline, and responsibilities. |
| [`AGENTS.md`](../../AGENTS.md) | Vendor-neutral AI Development governance: authority, lifecycle, context recovery, Git safety, quality gates, and reporting. |
| [Claude Code: Technical Settings](claude-code.md) | Tool-specific mechanics of `.claude/settings.json`; no general project rules. |
| [ADR Policy](../adr/README.md#when-an-adr-is-required) | When a new ADR is required, and when it isn't. |
| [Dependencies & Tooling](dependencies.md) | Runtime dependency baseline, dependency placement/versioning, and the upgrade process. |
| [Contributing](contributing.md) | Local setup and required quality commands. |
| [Pre-Commit & Local Code Quality Automation](pre-commit.md) | Local git hooks (pre-commit/pre-push), secret detection, the `uv-lock` hook, and the local quality check (`pre-commit run --all-files`). |
| [GitHub Actions: CI, Build & Release](ci.md) | Server-side CI, separate package verification, the protected release pipeline, actionlint, SHA-pinning, and Branch Protection recommendations. |
| [Repository Templates & Markdown Tooling](templates.md) | The pull request template, issue forms, document templates, Template Governance, and markdownlint. |
| [API Implementation Workflow](api-implementation-workflow.md) | The process for implementing a new LogRhythm API area. |

## What is and isn't automated yet

Formatting, linting, type checking, basic file hygiene, secret detection,
lockfile freshness, workflow linting, Markdown linting, and Conventional
Commit message validation are enforced both locally (git hooks, see
[Pre-Commit & Local Code Quality Automation](pre-commit.md)) and server-side
(see [GitHub Actions: CI, Build & Release](ci.md)) on every pull request and relevant
push; the full test suite runs before every push locally and as part of CI;
packaging is independently verified by a separate build workflow. A protected
release workflow validates release tags, reruns quality checks, builds and
verifies artifacts, publishes through OIDC Trusted Publishing, and creates a
GitHub Release only after successful PyPI publication. A pull request template
and GitHub Issue Forms now standardize contribution intake
(see [Repository Templates & Markdown Tooling](templates.md)). Tool-specific
permission settings may provide an additional mechanical backstop; see
[Claude Code: Technical Settings](claude-code.md) for the existing adapter.
What remains manual, applied by hand rather than configured by repository
tooling: actual branch protection, creation and protection of the `testpypi`
and `pypi` GitHub Environments, Trusted Publisher registration, release PR
merge, tag creation/push, and Environment approval.
