# Testing

## Layout

```text
tests/
├── conftest.py     Shared fixtures for the whole suite
├── unit/           Unit tests: no network, no external services
└── integration/    Integration tests: exercise the SDK against a real or
                     mocked LogRhythm instance (currently empty — added once
                     there is a transport layer to integrate)
```

## Running tests

```powershell
uv run pytest
```

This runs the full suite and reports coverage for `src/logrhythm_sdk`, including
missing lines. Coverage is measured and reported from this phase onward, but no hard
coverage gate is enforced yet.

## Coverage target

The long-term target for production code (everything under `src/logrhythm_sdk`,
excluding the initial scaffolding) is **at least 90% coverage**. This target will be
enforced once the SDK has enough real functionality for the number to be meaningful;
enforcing it during the foundation phase would only encourage tests written to pad
coverage rather than verify behavior.

## Test quality expectations

- Tests should assert real, meaningful behavior — not just "the import didn't raise."
- Unit tests must not perform real network calls; once a transport layer exists, unit
  tests mock it.
- Integration tests are allowed to depend on external state (e.g. a live or sandboxed
  LogRhythm instance) once that layer exists — they must never run implicitly as part
  of a default developer workflow that expects no network access.
- Test functions are exempt from the docstring requirement enforced elsewhere in the
  codebase (see `pyproject.toml`'s per-file Ruff ignores for `tests/**`); a clear test
  name is expected to carry that documentation instead.
