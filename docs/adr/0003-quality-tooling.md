# 0003. Ruff, mypy, and pytest as quality tooling; Google-style docstrings

## Status

Accepted

## Context

A professional SDK needs consistent formatting, linting, static type checking, and
automated tests from day one, so that quality expectations are enforced mechanically
rather than through review discipline alone. The tooling choice should minimize the
number of separate tools while still covering formatting, linting (including import
order, modernization, bug-prone patterns, and docstring conventions), typing, and
testing with coverage reporting.

## Decision

The project standardizes on:

- **Ruff** for both formatting and linting, with a rule selection covering
  pycodestyle, Pyflakes, isort, pyupgrade, flake8-bugbear, flake8-simplify,
  Ruff-specific rules, pydocstyle (Google convention), flake8-pytest-style, and
  exception-handling hygiene (flake8-blind-except, tryceratops).
- **mypy** in strict mode (untyped definitions disallowed, no implicit optionals,
  unused ignores and unreachable code flagged) targeting `src/logrhythm_sdk`.
- **pytest** with **pytest-cov** for tests and coverage reporting, targeting
  `src/logrhythm_sdk`, with missing lines shown.
- **Google-style docstrings** as the required docstring convention for all public
  modules, classes, and functions.

Rule selection is deliberately strict but not adversarial: it must not block normal,
readable Python constructs. Test files receive narrowly scoped exceptions (e.g. for
missing docstrings on individual test functions), since a descriptive test name
already documents intent.

## Consequences

- Formatting and most style debates are resolved automatically by Ruff rather than in
  review.
- Type errors, unreachable code, and unused type-ignores are caught before merge.
- All new public code must ship with type annotations and Google-style docstrings,
  which increases short-term authoring effort but keeps the codebase consistently
  documented as it grows.
- No coverage percentage is enforced yet; a long-term target (at least 90% for
  production code) is documented and will be enforced once the SDK has enough real
  functionality for the number to be meaningful.
