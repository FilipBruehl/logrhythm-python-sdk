# Repository Templates & Markdown Tooling

This page documents the repository's contribution templates (pull request,
issue forms, document templates) and Markdown linting. It complements
[Contributing](contributing.md), [Pull Requests](pull-requests.md), and
[Pre-Commit & Local Code Quality Automation](pre-commit.md).

## Template Governance

**Templates are exclusively a helper, never a normative source.** The binding
order is:

```text
SPEC / ADR / Workflow Documentation
        ↓
     Templates
```

If a template ever contradicts a SPEC, an ADR, or a workflow document under
`docs/development/`, the SPEC/ADR/workflow document is correct and the
**template is fixed** — never the other way around. A template cannot make an
architecture decision, close an Open Question, or override
[Architecture Governance](../../AGENTS.md#architecture-governance); it can
only prompt a contributor to check the documents that do.

## Available templates

| Template | Location | Purpose |
| --- | --- | --- |
| Pull request template | [`.github/pull_request_template.md`](../../.github/pull_request_template.md) | One shared template for every PR — see [Pull Requests](pull-requests.md). |
| Bug Report | [`.github/ISSUE_TEMPLATE/bug-report.yml`](../../.github/ISSUE_TEMPLATE/bug-report.yml) | Reporting unexpected/incorrect SDK behavior. |
| Feature Request | [`.github/ISSUE_TEMPLATE/feature-request.yml`](../../.github/ISSUE_TEMPLATE/feature-request.yml) | Proposing a new capability or behavior change. |
| API Endpoint | [`.github/ISSUE_TEMPLATE/api-endpoint.yml`](../../.github/ISSUE_TEMPLATE/api-endpoint.yml) | Planning/collaborating on one LogRhythm endpoint — see [API Endpoint issue](#api-endpoint-issue) below. |
| Issue chooser config | [`.github/ISSUE_TEMPLATE/config.yml`](../../.github/ISSUE_TEMPLATE/config.yml) | Disables blank issues; links to `SECURITY.md` and `CONTRIBUTING.md`. |
| ADR template | [`docs/templates/adr-template.md`](../templates/adr-template.md) | Skeleton matching the existing ADR structure — see [ADR Policy](../adr/README.md#when-an-adr-is-required). |
| Specification template | [`docs/templates/specification-template.md`](../templates/specification-template.md) | Skeleton matching SPEC-001 through SPEC-010's shape (SPEC-000 is exempt). |
| API Resource template | [`docs/templates/api-resource-template.md`](../templates/api-resource-template.md) | Describes one whole business resource — a helper for [API Implementation Workflow](api-implementation-workflow.md) step 3. |

All issue forms use GitHub's YAML Issue Forms format, per Scope — no
classic Markdown issue templates are used.

## API Endpoint issue

An API Endpoint issue ([`api-endpoint.yml`](../../.github/ISSUE_TEMPLATE/api-endpoint.yml))
is a **planning and collaboration tool**. It never replaces:

- [Design Specifications](../specifications/README.md),
- [ADRs](../adr/README.md),
- official LogRhythm documentation,
- the [API Coverage Matrix](../coverage/api-coverage.md), or
- tests.

### When to use it

- **Required**, when any of the following applies:
  - an external contributor is involved,
  - the endpoint needs shared planning,
  - architecture alignment is needed,
  - vendor information is being gathered collaboratively, or
  - the endpoint is large or unclear.
- **Recommended**, when any of the following applies:
  - the endpoint is complex,
  - several related endpoints are being implemented together,
  - vendor documentation is incomplete, or
  - open modeling questions remain.
- **Optional**, when all of the following apply:
  - the work is solo development,
  - the endpoint is fully documented by the vendor,
  - implementation is immediate, and
  - no architecture question is open.

This mirrors [API Implementation Workflow, API Endpoint issue](api-implementation-workflow.md#api-endpoint-issue),
which states the same rule at the point in the workflow where it applies.

## Relationship to SPECs and ADRs

Every template in this repository defers to the documents it helps produce or
reference:

- The **ADR template** does not restate when an ADR is required or its review
  process — see [ADR Policy](../adr/README.md#when-an-adr-is-required). It
  only provides the section skeleton.
- The **Specification template** does not restate the numbering scheme,
  status model, change process, or Review Criteria — see
  [Design Specifications](../specifications/README.md). Its own "Review
  Criteria" section is a self-check checklist referencing that page, not a
  duplicate of it.
- The **API Resource template** and **API Endpoint issue** do not replace
  [API Implementation Workflow](api-implementation-workflow.md)'s steps, the
  [API Coverage Matrix](../coverage/api-coverage.md), or vendor documentation
  — they help produce the artifacts those steps already call for.
- The **pull request template**'s Checklist restates items from
  [Definition of Done](definition-of-done.md) and
  [Pull Requests](pull-requests.md#required-pr-content) as checkboxes; the
  full rules for each item live on those pages, not in the template.

## Markdownlint

[markdownlint-cli2](https://github.com/DavidAnson/markdownlint-cli2) checks
Markdown style/consistency. It is check-only in this repository — **no
automatic `--fix` runs** as part of any hook or CI job.

### Configuration

Two files, no `package.json`, no npm dependency in the repository (the tool
runs inside pre-commit's own isolated Node environment, per
[Pre-Commit, Installation](pre-commit.md#installation)'s same reasoning for
other bootstrapped tools like gitleaks and actionlint):

- **`.markdownlint.jsonc`** — rule configuration. Starting point for this
  phase, adjusted only where a real repository-wide run showed a rule is
  unsuited to this project's documentation style (no blanket disabling):
  - `MD013` (line-length) — **disabled**. Prose wrapping in this repository
    is an authoring-style choice, not something meaningful to enforce at a
    fixed column count.
  - `MD024` (no-duplicate-heading) — restricted to **sibling headings only**.
    The SPEC/ADR series deliberately reuses generic subheadings (e.g.
    "Decision", "Consequences", "References") across independent documents
    and across unrelated sections within one document; that repetition is
    intentional structure, not a mistake. Restricting to siblings still
    catches a genuine duplicate under the same parent.
  - Every other rule is left at its default (enabled).
- **`.markdownlint-cli2.jsonc`** — tool configuration, not rule
  configuration. Sets `gitignore: true` (ignored files are never linted) and
  deliberately does **not** set a top-level `globs` — see
  [Pre-Commit integration](#pre-commit-integration) for why.

### Existing documentation cleanup

A full-repository run during this phase found 145 issues in 19 files: 142
were `MD060` (table column style) — this repository's tables pad cell content
with single spaces but left delimiter rows unpadded (`|---|---|` instead of
`| --- | --- |`), which is inconsistent with every supported table style.
These were fixed automatically (`--fix`; whitespace-only, no content or
heading changes). The remaining 3 were `MD051` (invalid link fragments) in
`docs/development/ci.md` — genuine broken anchors introduced by an earlier,
incorrect manual "fix" to a different link-checking script, corrected here
and cross-checked against markdownlint's actual (GitHub-compatible) anchor
algorithm. The whole repository is lint-clean as of this phase.

### Pre-Commit integration

The official hook, check-only (no `--fix` argument):

```yaml
- repo: https://github.com/DavidAnson/markdownlint-cli2
  rev: v0.23.2
  hooks:
    - id: markdownlint-cli2
      stages: [pre-commit]
```

This lints only the changed Markdown files passed to the hook — fast and
incremental, like the Ruff and mypy hooks. `.markdownlint-cli2.jsonc`
deliberately has no top-level `globs` entry: `globs` *appends* to whatever
files pre-commit already passed rather than replacing them, so setting it
would force every commit-time run to re-lint the entire repository.

A second hook entry provides `--fix`, but is bound to pre-commit's `manual`
stage — it is not part of `[pre-commit]` or `[pre-push]` and therefore never
runs automatically; a developer has to invoke it explicitly (see
[Manual full-repository lint](#manual-full-repository-lint)).

### Manual full-repository lint

To lint (check only) every Markdown file on demand:

```bash
uv run pre-commit run --all-files markdownlint-cli2
```

To **fix** what can be fixed automatically (table style and similar
mechanical issues) using the `manual`-stage hook — never run as part of a
git hook, always a deliberate step a developer chooses to run:

```bash
uv run pre-commit run --hook-stage manual --all-files
```

This runs the `markdownlint-cli2 (--fix)` hook, the only hook bound to the
`manual` stage. Always review the diff afterward — it should touch only
formatting (whitespace, table pipes), never content, headings, or
references. Treat it like any other auto-fixing hook output (see
[Pre-Commit, Troubleshooting](pre-commit.md#troubleshooting)).

### Exception process

No blanket rule disabling. If a specific rule proves genuinely unsuited to a
specific, legitimate pattern beyond what `MD013`/`MD024` already cover:

1. Fix the document first — most violations are genuine formatting slips.
2. If the pattern is intentional and repository-wide (not a one-off), propose
   a narrowly scoped adjustment to `.markdownlint.jsonc` (a specific rule
   option, not disabling the rule outright where avoidable) and state the
   reasoning in the change, the same way `MD013` and `MD024` are justified
   above.
3. For a genuine one-off exception, use an inline
   `<!-- markdownlint-disable-next-line MDxxx -->` comment rather than
   changing the global configuration.
4. No ADR is needed for a markdownlint rule adjustment — it is tooling
   configuration, not an architectural decision (see
   [ADR Policy](../adr/README.md#when-an-adr-is-not-required)).

## CI integration

Markdown linting runs in CI without any workflow change: the `quality` job in
[`.github/workflows/ci.yml`](../../.github/workflows/ci.yml) already runs
`uv run pre-commit run --all-files --show-diff-on-failure`, which now includes
the `markdownlint-cli2` hook alongside every other pre-commit-stage check —
see [GitHub Actions: CI & Build, CI Pipeline](ci.md#ci-pipeline-quality--test).
No new CI job was added.

## See also

- [Pull Requests](pull-requests.md)
- [Definition of Done](definition-of-done.md)
- [Pre-Commit & Local Code Quality Automation](pre-commit.md)
- [GitHub Actions: CI & Build](ci.md)
- [API Implementation Workflow](api-implementation-workflow.md)
- [ADR Policy](../adr/README.md#when-an-adr-is-required)
- [Design Specifications](../specifications/README.md)
