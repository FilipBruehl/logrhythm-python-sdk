# Design Principles

## Status

Draft.

This document consolidates rules already implied by the project's
[ADRs](../adr/README.md) and [Vision](../vision.md), and adds concrete
implementation-level conventions that future [Design Specifications](README.md) must
follow. It is a specification, not an ADR: it describes agreed working rules, not a
one-off architectural decision. Any rule below that turns out to be architecturally
significant enough to need its own rationale and history is still recorded separately
as an ADR under `docs/adr/`, per [CLAUDE.md](../../CLAUDE.md) — this document does not
replace that process.

## Purpose

Describe project-wide architecture and implementation rules once, in one place, so
that every future Design Specification can reference them instead of re-justifying
the same decisions repeatedly. This document does not describe any single component;
see [Component Model](../architecture/components.md) for that.

## Architecture principles

- **Composition over inheritance.** Components are assembled from smaller, injected
  parts rather than built through class hierarchies. Deep inheritance hides behavior
  in ancestor classes and makes components harder to reason about or replace
  independently. See [Component Model](../architecture/components.md).
- **Separation of concerns.** Transport, configuration, authentication, and
  API-specific logic are distinct concerns and stay in distinct components. Mixing
  them makes any one of them harder to change without affecting the others.
- **Single Responsibility Principle.** Each component has one reason to change. A
  component that both talks HTTP and parses domain models is doing two jobs and will
  need to change for two unrelated reasons.
- **High cohesion.** Code that changes together and reasons about the same concept
  lives together (for example, everything about one API's resources in that API's own
  module).
- **Low coupling.** Components depend on the minimum surface of other components they
  actually need — typically an injected dependency, not a concrete, hard-wired
  reference. This is what keeps `core` reusable across API modules.
- **Stable abstractions.** Where it measurably improves testability or
  maintainability, a component depends on a stable contract/abstraction rather than a
  concrete implementation — for example, code that needs to send HTTP requests should
  be written against a narrow, stable interface rather than a specific HTTP library's
  concrete client type, so the concrete implementation can be swapped or mocked
  without touching every caller. This principle exists in particular to support the
  future transport and HTTP architecture, where the concrete HTTP client is expected
  to sit behind such a contract. Abstractions are not introduced speculatively or
  "just in case" — **no speculative abstractions**: an abstraction is added when a
  concrete, present need for it exists (e.g. swappable transport, mockable
  infrastructure for tests), not in anticipation of a hypothetical future one.
- **Explicit over implicit.** Behavior is visible in the code path, not inferred from
  hidden state, monkey-patching, or "magic" defaults a reader cannot see.
- **Public API first.** Design decisions are made from the perspective of what a
  consumer of the SDK will see and depend on, not from what is most convenient to
  implement internally.
- **Dependency injection instead of global singletons.** Shared components
  (configuration, logger, transport) are created once by the composition root
  (`LogRhythmClient`) and passed to whoever needs them. Nothing reaches out to a
  global, ambient instance.
- **No global mutable state.** Global mutable state makes behavior depend on
  execution order and breaks test isolation; every piece of state lives inside an
  owning component instance.
- **Prefer small components.** A component with a narrow, well-named responsibility
  is easier to test, document, and eventually replace than a large one that does
  several things.

## API design

- **Consistent public API.** Every API module (Administration, AI Engine, Metrics,
  Alarm, Search, and later additions) exposes the same shape of client, resources,
  models, and filters, so a consumer who learns one module already knows the others.
- **Backwards compatibility.** Once a public component ships, its signature and
  behavior are a compatibility contract. Breaking it is a deliberate, documented, and
  versioned decision — never an accidental side effect of refactoring.
- **No surprises.** Public methods do what their name says and nothing more; side
  effects that are not obvious from the signature (e.g. silent network calls,
  mutation of caller-supplied objects) are avoided.
- **Do not alter vendor behavior.** The SDK reflects what the LogRhythm API actually
  does. It does not "fix", normalize, or reinterpret vendor responses in ways that
  would surprise someone cross-referencing the official documentation.
- **No invented API functionality.** The SDK never exposes an operation, field, or
  parameter that is not documented (or explicitly, observably confirmed) by
  LogRhythm. See
  [API Implementation Workflow](../development/api-implementation-workflow.md).

## Implementation principles

- **Readability over brevity.** Clear, slightly longer code beats a clever one-liner
  that takes longer to parse than to write.
- **Typing is mandatory.** All code under `src/logrhythm_sdk` is fully typed and
  checked with mypy in strict mode; see [CLAUDE.md](../../CLAUDE.md).
- **Google-style docstrings.** Every public module, class, and function documents
  itself in Google docstring format.
- **No hidden magic.** No metaclass tricks, dynamic attribute injection, or import-time
  monkey-patching that a reader cannot follow by reading the code in front of them.
- **No side effects on import.** Importing a module must not perform I/O, mutate
  global state, or have any observable effect beyond making names available.
- **No network access on import.** Nothing in the SDK contacts a network at import
  time; network access only happens as a result of an explicit call the consumer
  makes.
- **Fail fast.** Invalid input, missing configuration, or an unrecoverable error is
  raised immediately and explicitly, not swallowed or deferred to a confusing later
  failure.
- **Explicit resource management.** Anything that owns a resource requiring cleanup
  (e.g. an open connection) exposes an explicit, predictable way to release it (for
  example, a context manager or a `close()` method), rather than relying on garbage
  collection.

## Security principles

- **Security by default.** Safe behavior is the default; unsafe behavior requires an
  explicit, deliberate opt-in from the caller.
- **TLS verification on by default.** Once transport exists, certificate verification
  is always on unless a caller explicitly disables it. See
  [Architecture Overview](../architecture/overview.md).
- **Secrets are never logged.** Bearer tokens and other credentials never appear in
  log output, at any log level or format.
- **Secrets are never exposed via `repr()`.** Objects that hold a secret must not
  print or expose it through their default string representation, debugger output,
  or error messages.
- **Prefer secure defaults.** Where a choice must be made and the specification is
  silent, the more secure option is the default; the less secure option must be
  requested explicitly.

## Testability

- **Dependency injection.** Because shared components are injected rather than
  constructed internally, tests can substitute fakes or mocks without patching
  internals.
- **Mockable infrastructure.** Transport and other I/O boundaries are designed so
  that unit tests can substitute a mock without needing real network access.
- **Deterministic behavior.** Given the same inputs and mocked dependencies, a
  component's behavior is repeatable; tests do not depend on wall-clock time, network
  timing, or external state unless that is exactly what is being tested.
- **Unit tests without network access.** Unit tests never perform a real network
  call. See [Testing](../development/testing.md).
- **Integration tests are kept separate.** Tests that exercise a real or mocked
  LogRhythm instance live under `tests/integration/`, distinct from `tests/unit/`.

## Documentation principles

- **Architecture before implementation.** The shape of a component is designed and
  reviewed (in a Design Specification) before it is implemented.
- **An ADR explains the why.** Architecture Decision Records capture the reasoning
  and trade-offs behind a significant, durable decision. See
  [docs/adr/README.md](../adr/README.md).
- **A Design Specification describes the how.** Specifications translate an accepted
  decision into a concrete, implementable design. See
  [Design Specifications](README.md).
- **User documentation describes only what is implemented.** README, `/docs` guides,
  and docstrings describe available functionality only — never planned or in-progress
  functionality as if it already worked.
- **Target architecture and implementation status are always clearly separated.**
  Every document that describes planned work says so explicitly (as this document,
  the [Component Model](../architecture/components.md), and the
  [Architecture Overview](../architecture/overview.md) all do).

## Extensibility

- **New API modules follow the same architecture.** Any newly implemented API area
  reuses the same module shape (models, filters, resources, client) described in
  [Component Model](../architecture/components.md) — it does not introduce a
  parallel structure.
- **Shared infrastructure belongs in `core`.** If two or more API modules would need
  the same piece of logic, that logic belongs in `logrhythm_sdk.core`, not duplicated
  or reinvented per module.
- **API-specific logic stays in its own module.** Logic specific to one LogRhythm API
  area is never added to `core` or to another API module.

## Non-goals

These are implementation-level anti-patterns this document rules out; for the
project's higher-level, product-scope non-goals (what the SDK itself is not trying to
be), see [Vision](../vision.md#non-goals).

The project explicitly does not want, and will actively avoid:

- **Global singletons** — every shared component is owned and injected by the
  composition root, never reached through global/ambient access.
- **Hidden side effects** — no component does something a reader would not expect
  from its public signature.
- **Implicit configuration** — configuration is always explicit and traceable to a
  source (file, argument, or documented default); nothing is inferred silently from
  the environment.
- **Untested production code** — code under `src/logrhythm_sdk` ships with tests that
  verify real behavior.
- **Invented vendor functionality** — the SDK never fills a documentation gap with a
  guess about what LogRhythm's API "probably" does.
- **Unnecessary complexity** — a simpler design that meets the same requirement is
  always preferred over a more general or abstract one that does not yet have a
  concrete need.
