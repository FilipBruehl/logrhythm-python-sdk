# Dependencies & Tooling

This page documents the SDK's runtime dependency baseline, how dependencies are
placed and versioned, and how future dependency upgrades are handled. It
complements [Contributing](contributing.md) (local setup) and the
[ADR Policy](../adr/README.md#when-an-adr-is-required) (when a dependency change
needs its own ADR).

## Runtime dependencies

| Dependency | Version range | Used for | Decision |
|---|---|---|---|
| `pydantic` | `>=2.9,<3` | The SDK's exclusive model layer (public and internal, request and response). | [ADR-0005](../adr/0005-pydantic-v2-models.md) |
| `httpx` | `>=0.27,<1` | The SDK's sole underlying HTTP library, fully encapsulated behind `Transport`. | [ADR-0006](../adr/0006-httpx-transport.md) |
| `pyyaml` | `>=6.0,<7` | Parsing YAML configuration files (safe-loading only). | [ADR-0007](../adr/0007-configuration-file-formats.md) |

Each range pairs a compatible lower bound with an upper major-version boundary —
the SDK is expected to work with any version satisfying the range, and a new
major release of any of these libraries requires a deliberate evaluation (see
[Dependency upgrades](#dependency-upgrades)) before the upper bound is raised.

JSON and TOML configuration support add no dependency: JSON uses the standard
library's `json` module, and TOML uses the standard library's `tomllib`
(available for the SDK's Python 3.13+ baseline) — see
[ADR-0007](../adr/0007-configuration-file-formats.md).

No further runtime dependencies exist at this phase.

## Dependency placement

- **Runtime dependencies** belong in `[project.dependencies]` in
  `pyproject.toml` — this is what a consumer installing the SDK also installs.
- **Development tools** (Ruff, mypy, pytest, pytest-cov) remain in
  `[dependency-groups.dev]` — these are never installed for a consumer of the
  published package, only for local development.
- **`uv.lock` is versioned** in the repository. `pyproject.toml` describes
  *compatibility* (the version ranges above); `uv.lock` describes the exact,
  reproducible set of resolved versions used for local development — both
  files are committed, and both are kept in sync via `uv sync` / `uv lock`.

## Dependency upgrades

- An upgrade is its own dedicated commit (and, per
  [Branch Strategy](branching.md), typically its own `fix/*` or `feature/*`
  branch) — `chore(deps): ...` per [Commit Strategy](commits.md) — never
  bundled with unrelated feature or fix work.
- After upgrading, all four required quality commands
  (`ruff format --check`, `ruff check`, `mypy`, `pytest`) must still pass
  before the change is considered done.
- The upgraded dependency's release notes/changelog are checked for breaking
  changes before the upgrade is merged.
- A **major**-version upgrade (e.g. Pydantic 2 → 3, httpx 0.x → 1.x, PyYAML
  6 → 7) is evaluated via a new ADR before being adopted, per
  [ADR Policy](../adr/README.md#when-an-adr-is-required) — it is not a routine
  dependency bump, since it reverses or replaces a decision already recorded in
  [ADR-0005](../adr/0005-pydantic-v2-models.md),
  [ADR-0006](../adr/0006-httpx-transport.md), or
  [ADR-0007](../adr/0007-configuration-file-formats.md).
- A minor/patch upgrade within an already-accepted range does not need a new
  ADR.

## Python baseline

- **Python 3.13 remains the binding minimum supported version**, per
  [ADR-0001](../adr/0001-python-313.md). This is not lowered to support older
  Python versions.
- `typing` is used exclusively from the standard library; `typing_extensions`
  is **not** a direct project dependency.
- Modern Python 3.13 syntax and standard-library features may be used where
  they improve clarity, consistent with [ADR-0001](../adr/0001-python-313.md).

## Pydantic mypy plugin

The official Pydantic mypy plugin (`pydantic.mypy`) is enabled in
`pyproject.toml` so static type checking understands Pydantic's generated
`__init__` and aliasing behavior correctly, per
[ADR-0005](../adr/0005-pydantic-v2-models.md). Enabled options:

- `init_typed`
- `init_forbid_extra`
- `warn_required_dynamic_aliases`

No further mypy plugins are added at this phase.

## Configuration file formats

Version 1 supports YAML (`.yaml`/`.yml`, via PyYAML, safe-loading only), JSON
(`.json`, via the standard library), and TOML (`.toml`, via `tomllib`). Format
is determined exclusively by file extension — never by inspecting file
content or any other heuristic — and an unrecognized extension is rejected.
See [ADR-0007](../adr/0007-configuration-file-formats.md) and
[SPEC-002, Configuration Sources](../specifications/configuration.md#configuration-sources)
for the full, binding decision.

## See also

- [ADR-0005 — Use Pydantic v2 for SDK models](../adr/0005-pydantic-v2-models.md)
- [ADR-0006 — Use HTTPX as HTTP transport library](../adr/0006-httpx-transport.md)
- [ADR-0007 — Support YAML, JSON, and TOML configuration files](../adr/0007-configuration-file-formats.md)
- [ADR Policy](../adr/README.md#when-an-adr-is-required)
- [Commit Strategy](commits.md)
- [Contributing](contributing.md)
