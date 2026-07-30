# API Implementation Workflow

This document describes the process to follow when implementing support for a new
LogRhythm API area (e.g. Alarm API, Search API). It is a process description for
future work; no API area is implemented yet as part of this foundation phase.

> **No guessing.** If official documentation for a behavior, field, parameter, or
> error case is unclear, incomplete, or missing, that gap must be written down
> explicitly (in the implementation spec, docstrings, and/or `docs/`). It must never
> be filled in with an assumption. An honestly incomplete implementation is preferred
> over a confident, invented one.

## Steps

1. **Capture the official documentation page.** Record which LogRhythm documentation
   page(s) the implementation is based on, including version/date if available.
2. **Extract facts, schemas, parameters, and uncertainties.** Pull out endpoints,
   request/response schemas, required and optional parameters, authentication
   requirements, and error behavior. Explicitly list anything that is ambiguous or
   undocumented.
3. **Create a compressed Markdown implementation spec.** Summarize step 2 into a
   concise spec that will drive the implementation, stored alongside the relevant
   development materials.
4. **Define the SDK mapping.** Decide how the documented API maps onto the SDK's
   conventions: module name, models, filters, resource methods, and client methods.
5. **Implement models, filters, resources, and client integration.** Follow the
   established shape (see [Architecture Overview](../architecture/overview.md))
   consistently with existing API modules.
6. **Write unit tests with mocked HTTP calls.** No test in this phase depends on a
   live LogRhythm instance.
7. **Update documentation and API coverage.** Reflect the newly implemented endpoints
   in `/docs`, including any documented gaps or limitations carried over from step 2.
8. **Run Ruff, mypy, and pytest.** All must pass:

   ```powershell
   uv run ruff format --check .
   uv run ruff check .
   uv run mypy src/logrhythm_sdk
   uv run pytest
   ```

9. **Review the diff.** Confirm the change is scoped to the API area being
   implemented and does not drift into unrelated files.
10. **Commit a small, reviewable change.** Prefer one focused commit (or a small,
    logically ordered series) over one large, hard-to-review change.
