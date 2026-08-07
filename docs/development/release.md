# Release & Publishing

This page is the binding release and publishing guide. Build, release, and
publish remain separate processes:

```text
Validate
    |
    v
Quality
    |
    v
Build
    |
    v
Verify
    |
    v
Publish
    |
    v
GitHub Release
```

The ordinary [Build workflow](ci.md#build-workflow-build-with-verification)
never publishes. Only [`.github/workflows/release.yml`](../../.github/workflows/release.yml)
can publish, and only through a configured GitHub Environment and OpenID
Connect (OIDC) Trusted Publisher.

## Versioning strategy

The project uses [Semantic Versioning](https://semver.org/) release numbers
represented as Python-compatible version strings.

- `pyproject.toml` `[project].version` is the single canonical source of truth.
- `src/logrhythm_sdk/__init__.py` exposes a static `__version__` mirror for
  runtime users.
- Built wheel and source-distribution metadata are derived from
  `pyproject.toml`.
- The release pipeline requires `pyproject.toml`, `uv version --short`,
  `__version__`, built package metadata, and the release tag to agree.
- Git tags use `v<version>`.

Examples:

```text
v0.1.0
v1.2.3
v0.5.0rc1
```

Update the canonical version with uv:

```powershell
uv version 0.2.0
```

`uv version` updates `pyproject.toml` and refreshes project state. The same
release-preparation change must update the `__version__` mirror to the exact
same value. Check the result with:

```powershell
uv version --short
uv run --locked python .github/scripts/validate_release.py --tag v0.2.0
```

### Versioning before 1.0

The `0.x` series indicates that the public API is not yet stable, but breaking
changes are still deliberate and documented:

- increment the minor version (`0.Y.0`) for a feature release or an intentional
  compatibility break;
- increment the patch version (`0.Y.Z`) only for backward-compatible fixes;
- identify every breaking change explicitly in the release PR and changelog;
- never use pre-1.0 status as permission for silent or incidental breakage.

Starting with `1.0.0`, normal Semantic Versioning major/minor/patch rules apply.

### Pre-releases

Alpha, beta, and release-candidate versions use PEP 440 syntax:

| Stage | Version | Tag |
| --- | --- | --- |
| Alpha | `0.2.0a1` | `v0.2.0a1` |
| Beta | `0.2.0b1` | `v0.2.0b1` |
| Release candidate | `0.2.0rc1` | `v0.2.0rc1` |

A production tag for a pre-release deliberately publishes it to PyPI. The
`pypi` Environment approval is the final human gate. Its GitHub Release is
marked as a pre-release and is not marked as the latest stable release.

## Changelog and release notes

[`CHANGELOG.md`](../../CHANGELOG.md) follows
[Keep a Changelog](https://keepachangelog.com/) and uses the categories
Added, Changed, Deprecated, Removed, Fixed, and Security.

- Changes accumulate under `Unreleased`.
- A release PR moves relevant entries into a dated `## [<version>] - YYYY-MM-DD`
  section.
- Each release version appears exactly once as a dated section.
- The section must contain at least one real list entry.
- Release notes are curated in the changelog; they are not generated from
  commits or pull-request titles.
- The workflow copies the curated version section into the GitHub Release. It
  does not generate or rewrite the content.

## Release preparation pull request

Every release is prepared on its own `feature/*` branch created from `main`,
for example:

```text
feature/prepare-0.1.0
```

The release PR contains only release-preparation changes:

- canonical version in `pyproject.toml`;
- matching `__version__` mirror and lockfile state;
- dated `CHANGELOG.md` section and curated release notes;
- packaging metadata changes, when applicable;
- results of every required quality, build, and verification check;
- explicit compatibility and pre-release status.

The PR follows the ordinary [Pull Request](pull-requests.md) and
[Definition of Done](definition-of-done.md) requirements. A human reviews and
merges it before any tag is created.

## Local release validation

Run the full quality gates without relying on an earlier CI result:

```powershell
uv sync
uv run ruff format --check .
uv run ruff check .
uv run mypy src/logrhythm_sdk
uv run pytest
uv run pre-commit run --all-files
uv run pre-commit run --hook-stage pre-push --all-files
```

Build with local source overrides disabled:

```powershell
uv build --no-sources
uv venv .verify-venv
$wheel = Get-ChildItem dist/*.whl -ErrorAction Stop
uv pip install --python .verify-venv $wheel.FullName
uv run python .github/scripts/verify_package.py `
  --installed-python .verify-venv/Scripts/python.exe
```

On POSIX runners, the verification interpreter is
`.verify-venv/bin/python`. `verify_package.py` is shared by `build.yml` and
`release.yml`; its checks are never duplicated inline.

## Release workflow triggers

The Release workflow supports two triggers.

### Production tag

A pushed `v*` tag selects `pypi`. The validator requires the tag to match the
canonical version and its commit to be contained in `main`. After the protected
`pypi` Environment is approved, the exact verified artifacts are published and
then attached to a GitHub Release.

### Manual workflow dispatch

`workflow_dispatch` has a required target choice:

- `testpypi`: optional test publication from `main`; no GitHub Release is
  created;
- `pypi`: manual retry or emergency continuation from an existing release tag;
  it is not a tag-creation shortcut.

Both paths perform validation, quality checks, build, and verification again.
Manual dispatch never bypasses an Environment or Trusted Publisher.

## Release pipeline

The workflow has five dependent jobs:

```text
validate-release
       |
       v
quality-test
       |
       v
build-verify
       |
       v
publish
       |
       v
github-release
```

- **`validate-release`** checks tag syntax, supported version syntax,
  `pyproject.toml`, `uv version`, `__version__`, changelog presence, and that
  the commit belongs to `main`.
- **`quality-test`** reruns Ruff formatting, Ruff linting, mypy, and pytest.
- **`build-verify`** runs `uv build --no-sources`, creates a wheel and source
  distribution, reuses `verify_package.py`, creates `SHA256SUMS`, and stores
  the verified artifacts plus curated release notes.
- **`publish`** downloads and checksum-verifies those exact artifacts, enters
  `testpypi` or `pypi`, obtains a short-lived OIDC credential, and calls
  `uv publish`.
- **`github-release`** runs only for PyPI after `publish` succeeds. It creates
  the release from the existing tag and attaches the wheel, source
  distribution, `SHA256SUMS`, and curated release notes.

## Trusted Publishing and GitHub Environments

Repository administrators configure two GitHub Environments manually under
**Settings → Environments**. The workflow does not create or modify them.

### `pypi`

- Configure required human reviewers before deployment.
- Restrict deployment to protected `v*` tags.
- Configure the PyPI project Trusted Publisher for this repository,
  `.github/workflows/release.yml`, and the exact environment name `pypi`.
- Keep this Environment protected; production publication must never proceed
  without its manual approval.

### `testpypi`

- Configure a separate Environment named `testpypi`.
- Configure the Trusted Publisher independently on TestPyPI with the exact
  repository, workflow, and environment name.
- Review protection is recommended even though TestPyPI publication is
  optional.

The `publish` job has only:

```yaml
permissions:
  contents: read
  id-token: write
```

No API token, username, password, `twine`, or PyPI publishing action is used.
Every non-publishing job defaults to `contents: read`; the final
`github-release` job receives only the technically necessary `contents: write`
permission for creating the release and uploading its assets.

## Production release procedure

Only a human owner performs the external release actions:

1. Create `feature/prepare-<version>` from `main`.
2. Update the version with `uv version`, synchronize `__version__`, and update
   `CHANGELOG.md` plus any packaging metadata.
3. Run all quality, build, package-verification, link, and workflow checks.
4. Open and review the dedicated release PR.
5. Merge the release PR into `main`.
6. Create an annotated `v<version>` tag on the resulting commit on `main`.
7. Push only that tag.
8. Review the `validate-release`, `quality-test`, and `build-verify` results.
9. Approve the protected `pypi` Environment.
10. Confirm `uv publish` succeeds.
11. Confirm the GitHub Release contains the wheel, source distribution,
    `SHA256SUMS`, and curated release notes.
12. Perform an installation and import test from the published registry.

Example human-operated tag commands:

```powershell
git tag -a v0.1.0 -m "v0.1.0"
git push origin v0.1.0
```

## Installation test

For a production release:

```powershell
uv venv .release-install-test
uv pip install --python .release-install-test logrhythm-python-sdk==0.1.0
.release-install-test/Scripts/python.exe -c `
  "import logrhythm_sdk; print(logrhythm_sdk.__version__)"
```

For TestPyPI, install runtime dependencies from PyPI first, then install the
test artifact without dependencies from TestPyPI:

```powershell
uv venv .release-install-test
uv pip install --python .release-install-test `
  "pydantic>=2.9,<3" "httpx>=0.27,<1" "pyyaml>=6.0,<7"
uv pip install --python .release-install-test --no-deps `
  --default-index https://test.pypi.org/simple/ `
  logrhythm-python-sdk==0.1.0
```

Use `.release-install-test/bin/python` instead of the Windows path on POSIX.

## AI Coding Agent responsibility

An AI Coding Agent may, when explicitly authorized:

- prepare the release-preparation `feature/prepare-<version>` branch contents;
- update and validate version mirrors, changelog, metadata, and release notes;
- run quality, build, verification, link, and workflow checks;
- document the proposed release and report readiness.

An AI Coding Agent never:

- merges the release PR;
- creates or pushes a release tag;
- starts or reruns the Release workflow;
- approves a GitHub Environment;
- invokes registry publishing;
- creates the GitHub Release.

These external actions remain human-owned even when every validation passes.

## Deferred extensions

The following are deliberately not implemented:

- artifact attestations;
- automatic changelog generation;
- automatic release-note generation;
- dynamic Git-derived versioning.

`uv publish --no-attestations` makes the current artifact-attestation boundary
explicit. Future adoption requires a separately reviewed infrastructure change.

## See also

- [GitHub Actions: CI, Build & Release](ci.md)
- [Developer Workflow](workflow.md)
- [Definition of Done](definition-of-done.md)
- [Commit Strategy](commits.md)
- [Branch Types & Branch Strategy](branching.md)
- [`AGENTS.md`](../../AGENTS.md) for AI Coding Agent authority.
