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

## Testing rules by change type

No test implementations are prescribed here — this section states the rule that
applies to each category of change; the tests themselves are written as part of
the work, per [Definition of Ready](definition-of-ready.md) and
[Definition of Done](definition-of-done.md#tests).

- **New features (`feat`)** — new tests cover the documented behavior, its
  edge cases, and its error paths. A feature is not done without tests that
  exercise it directly, not just as a side effect of some other test.
- **Bugfixes (`fix`)** — a regression test that fails before the fix and
  passes after it is added in the same change (see the "Regression tests" rule
  below). The test's name or docstring describes the failure it guards
  against.
- **Refactoring (`refactor`)** — existing tests continue to pass unchanged in
  their expectations. A "refactor" that requires changing what a test asserts
  (beyond call-site renames) is not a pure refactor — it changes behavior, and
  should be re-scoped or explicitly justified as such.
- **Documentation-only changes (`docs`)** — no test changes are required.
  Code examples that look executable must be clearly marked as illustrative or
  pseudocode (consistent with how the SPEC series marks its own examples), so
  they are never mistaken for a tested contract.
- **Regression tests** — every bug fix gets a permanent regression test that
  stays in the suite. A regression test is never deleted as "no longer
  relevant" without documenting, in the same change, why the underlying risk
  no longer applies.
- **Test data** — placeholder values only: hosts, credentials, tokens, and
  certificates used in tests are never real, and never resemble real
  production identifiers. This restates, for tests specifically, the
  repository-wide rule against committing real secrets (see
  [CLAUDE.md](../../CLAUDE.md), "Security requirements").
- **Vendor/manufacturer data** — tests never embed captured real vendor
  response data that could contain customer-identifiable or otherwise
  sensitive information. Only documented, synthetic, or explicitly sanitized
  fixtures are used, and synthetic fixtures are clearly marked as such —
  consistent with [SPEC-010's Testing section](../specifications/api-modules.md#testing)
  and [SPEC-000](../specifications/design-principles.md#api-design)'s "No
  invented API functionality" principle (a synthetic fixture may only use
  documented fields, never invented ones).
