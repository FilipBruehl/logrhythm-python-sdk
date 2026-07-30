# Vision

## Long-term vision

`logrhythm-python-sdk` aims to become the reference typed Python client for LogRhythm's
SIEM REST APIs: a single, coherent SDK that lets Python developers and security teams
integrate with LogRhythm without re-implementing HTTP plumbing, authentication, or
response parsing for every project.

The SDK is intended to eventually cover, at minimum:

1. Administration API
2. AI Engine API
3. Metrics API
4. Alarm API
5. Search API
6. Further APIs as they are implemented in later phases

## Target audience

- Security engineers and SOC teams automating LogRhythm operations from Python.
- Integration and platform engineers building tooling around LogRhythm.
- Developers who need a typed, IDE-friendly client instead of hand-rolled HTTP calls.

## Project goals

- Provide a single, consistent, typed entry point to LogRhythm's REST APIs.
- Keep every API module structurally consistent (models, filters, resources, client).
- Make the public API predictable, well documented, and safe to depend on.
- Treat security (TLS verification, secret handling) as a default, not an opt-in.
- Base every implemented behavior on LogRhythm's official, documented API behavior.

## Non-goals

- The SDK is not a general-purpose SIEM abstraction layer for multiple vendors.
- The SDK does not attempt to replicate the LogRhythm web UI or its workflows.
- The SDK will not guess at, infer, or "fill in" undocumented API behavior.
- Asynchronous support, a CLI, or a plugin system are not goals for the initial phases;
  they may be considered later as optional, separate extensions.

## Design philosophy

- **Public APIs over internal convenience.** Internal refactors must not leak into or
  destabilize the public surface.
- **Readability over brevity.** Explicit, slightly longer code is preferred over clever
  shortcuts.
- **Explicit over implicit.** Behavior should be visible in the code, not inferred from
  side effects or hidden defaults.
- **Composition over inheritance.** API modules are composed from shared `core`
  building blocks rather than built through deep class hierarchies.
- **Security over comfort.** Safe defaults (TLS verification enabled, secrets never
  logged) take priority over convenience shortcuts.

## Quality standard

Every publicly visible component is expected to ship with:

- Full type annotations, checked with mypy in strict mode.
- Google-style docstrings.
- Tests that exercise real behavior, not just coverage padding.
- Corresponding documentation under `/docs`.

## Stable public API

Once an API module is released, its public surface (client methods, models, and
exceptions) is treated as a compatibility contract. Breaking changes are deliberate,
documented, and versioned — not incidental side effects of internal refactoring.

## Documentation-driven implementation

Every LogRhythm API module is implemented from LogRhythm's official documentation.
Where documentation is missing, ambiguous, or contradictory, the SDK will:

- Document the gap explicitly (in code comments, docstrings, or `/docs`), and
- Avoid inventing behavior that has not been observed or documented.

Undocumented vendor behavior is never guessed at to make an implementation feel more
complete than it actually is.
