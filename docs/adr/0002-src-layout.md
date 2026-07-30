# 0002. `src` layout and package namespace

## Status

Accepted

## Context

The project needs a package layout and an import name. Two common layouts exist for
Python packages: a flat layout (package directory at the repository root) and a `src`
layout (package directory nested under `src/`). The flat layout can accidentally
import the in-repo source instead of the installed package during testing, which
hides packaging mistakes. The project also needs a stable, unambiguous import name
distinct from its distribution name.

## Decision

The project uses a `src` layout. The importable package lives at
`src/logrhythm_sdk/` and is imported as `logrhythm_sdk`. The PyPI/distribution name
is `logrhythm-python-sdk`. A `py.typed` marker file is included so type checkers
recognize the package as typed (PEP 561).

## Consequences

- Tests and tooling always exercise the installed package, not an accidentally
  importable source directory, reducing the risk of "works in dev, broken when
  installed" bugs.
- Consumers get inline type information via `py.typed` without needing separate
  stub packages.
- The distribution name (`logrhythm-python-sdk`) and import name (`logrhythm_sdk`)
  differ, which is normal for Python packaging but must be kept consistent across
  `pyproject.toml`, documentation, and examples.
