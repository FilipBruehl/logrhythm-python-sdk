# 0004. Markdown documentation under `/docs` and Architecture Decision Records

## Status

Accepted

## Context

An SDK that will eventually cover multiple LogRhythm API areas needs a place to
record both the target architecture and the reasoning behind decisions that shape it,
so that later contributors (human or AI-assisted) do not have to reverse-engineer
intent from code alone. The project also wants to defer choosing a documentation
site generator until there is enough real content to justify one.

## Decision

Project documentation is written as plain Markdown under `/docs`, covering vision,
architecture, and development process. Significant architecture decisions are
recorded as Architecture Decision Records (ADRs) under `docs/adr/`, using a
consistent format (Title, Status, Context, Decision, Consequences). A documentation
site generator (e.g. MkDocs) is explicitly out of scope for this phase and is left
for a later, separate decision.

## Consequences

- Documentation is readable directly from the repository (e.g. on GitHub) without
  additional tooling or a build step.
- Significant decisions have a durable, discoverable record instead of living only in
  commit messages or chat history.
- Introducing a documentation site generator later remains possible and should not
  require restructuring the existing Markdown content, but the specific tool and
  configuration are deferred to their own future decision.
