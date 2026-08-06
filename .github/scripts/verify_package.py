"""Verify a built ``logrhythm-python-sdk`` distribution.

Infrastructure helper shared by the build and release workflows (see
``.github/workflows/build.yml``, ``.github/workflows/release.yml``, and
``docs/development/ci.md``). It is not part of the published SDK and is
never imported by it. It uses only the Python standard library — no new
dependency, runtime or development, is introduced for this check.

Checks performed:

- The wheel and source distribution both exist in ``dist/``.
- The source distribution contains the package source.
- The wheel contains ``logrhythm_sdk/__init__.py`` and
  ``logrhythm_sdk/py.typed``.
- The wheel contains no test, cache, or local-settings artifacts.
- The wheel's declared runtime dependencies match ``pyproject.toml``.
- The wheel installs cleanly into a fresh, isolated environment, the package
  imports successfully, ``__version__`` can be read, and it matches both the
  installed distribution metadata and ``pyproject.toml``'s version.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tarfile
import tomllib
import zipfile
from pathlib import Path

# Path fragments that must never appear in a distributed wheel: development,
# test, and local-environment artifacts that would indicate an unclean build.
FORBIDDEN_SUBSTRINGS = (
    "tests/",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    ".git/",
    ".claude",
    ".coverage",
    "__pycache__",
    "htmlcov",
    ".pre-commit-config.yaml",
)

REQUIRED_WHEEL_MEMBERS = (
    "logrhythm_sdk/__init__.py",
    "logrhythm_sdk/py.typed",
)


def fail(message: str) -> None:
    """Print a failure message to stderr and exit non-zero."""
    print(f"FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def ok(message: str) -> None:
    """Print a success message to stdout."""
    print(f"OK: {message}")


def find_one(directory: Path, pattern: str) -> Path:
    """Return the single file in ``directory`` matching ``pattern``."""
    matches = sorted(directory.glob(pattern))
    if len(matches) != 1:
        fail(f"expected exactly one {pattern!r} in {directory}, found {matches}")
    return matches[0]


def check_sdist(sdist_path: Path) -> None:
    """Verify the source distribution exists and contains the package."""
    if not sdist_path.is_file():
        fail(f"source distribution not found: {sdist_path}")
    ok(f"source distribution present: {sdist_path.name}")

    with tarfile.open(sdist_path) as tar:
        names = tar.getnames()
    if not any(name.endswith("src/logrhythm_sdk/__init__.py") for name in names):
        fail("source distribution does not contain src/logrhythm_sdk/__init__.py")
    ok("source distribution contains the package source")


def check_wheel_contents(wheel_path: Path) -> zipfile.ZipFile:
    """Verify the wheel exists, contains required members, and nothing extra."""
    if not wheel_path.is_file():
        fail(f"wheel not found: {wheel_path}")
    ok(f"wheel present: {wheel_path.name}")

    zf = zipfile.ZipFile(wheel_path)
    names = zf.namelist()

    for member in REQUIRED_WHEEL_MEMBERS:
        if member not in names:
            fail(f"wheel is missing required member: {member}")
        ok(f"wheel contains {member}")

    forbidden = [name for name in names for fragment in FORBIDDEN_SUBSTRINGS if fragment in name]
    if forbidden:
        fail(f"wheel contains development/test artifacts: {forbidden}")
    ok("wheel contains no test, cache, or local-settings artifacts")

    return zf


def _normalize_requirement(spec: str) -> tuple[str, frozenset[str]]:
    """Split a requirement string into (normalized name, constraint parts).

    Handles the fact that installers may reorder comma-separated specifiers
    (e.g. ``pydantic>=2.9,<3`` may appear as ``pydantic<3,>=2.9`` in wheel
    metadata) without needing the ``packaging`` library.
    """
    for i, ch in enumerate(spec):
        if ch in "<>=!~":
            name, constraints = spec[:i], spec[i:]
            break
    else:
        name, constraints = spec, ""
    normalized_name = name.strip().lower().replace("_", "-")
    parts = frozenset(part.strip() for part in constraints.split(",") if part.strip())
    return normalized_name, parts


def check_wheel_metadata(zf: zipfile.ZipFile, pyproject_path: Path) -> None:
    """Verify the wheel's Requires-Dist entries match pyproject.toml."""
    metadata_name = next((n for n in zf.namelist() if n.endswith(".dist-info/METADATA")), None)
    if metadata_name is None:
        fail("wheel does not contain a .dist-info/METADATA file")
    metadata = zf.read(metadata_name).decode("utf-8")

    with pyproject_path.open("rb") as f:
        pyproject = tomllib.load(f)
    declared_dependencies = pyproject["project"]["dependencies"]

    requires_dist = [
        line.removeprefix("Requires-Dist:").strip()
        for line in metadata.splitlines()
        if line.startswith("Requires-Dist:")
    ]
    requires_dist_by_name = dict(_normalize_requirement(r) for r in requires_dist)

    for dependency in declared_dependencies:
        name, parts = _normalize_requirement(dependency)
        if name not in requires_dist_by_name:
            fail(f"wheel metadata is missing runtime dependency: {name}")
        if requires_dist_by_name[name] != parts:
            fail(
                f"wheel metadata for {name!r} has {sorted(requires_dist_by_name[name])}, "
                f"expected {sorted(parts)} (from pyproject.toml)"
            )
        ok(f"wheel metadata declares {dependency!r} correctly")


def check_installed(python_exe: Path, expected_version: str) -> None:
    """Verify the wheel, once installed in isolation, imports and reports correctly."""
    if not python_exe.is_file():
        fail(f"isolated environment interpreter not found: {python_exe}")

    snippet = (
        "import logrhythm_sdk, importlib.metadata as m; "
        "installed = m.version('logrhythm-python-sdk'); "
        "assert logrhythm_sdk.__version__ == installed, "
        "(logrhythm_sdk.__version__, installed); "
        "print(logrhythm_sdk.__version__)"
    )
    result = subprocess.run(
        [str(python_exe), "-c", snippet],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        fail(
            "import/version check failed in the isolated environment:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
    printed_version = result.stdout.strip().splitlines()[-1]
    if printed_version != expected_version:
        fail(
            f"installed logrhythm_sdk.__version__ ({printed_version}) does not "
            f"match pyproject.toml's version ({expected_version})"
        )
    ok(
        "wheel installs cleanly in an isolated environment; import succeeds; "
        f"__version__ == installed metadata version == pyproject.toml version "
        f"({printed_version})"
    )


def main() -> None:
    """Run every package-verification check, failing fast on the first problem."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist-dir", type=Path, default=Path("dist"))
    parser.add_argument("--pyproject", type=Path, default=Path("pyproject.toml"))
    parser.add_argument(
        "--installed-python",
        type=Path,
        required=True,
        help="Interpreter of a fresh, isolated environment the wheel was installed into.",
    )
    args = parser.parse_args()

    wheel_path = find_one(args.dist_dir, "*.whl")
    sdist_path = find_one(args.dist_dir, "*.tar.gz")

    with args.pyproject.open("rb") as f:
        pyproject = tomllib.load(f)
    expected_version = pyproject["project"]["version"]

    check_sdist(sdist_path)
    zf = check_wheel_contents(wheel_path)
    check_wheel_metadata(zf, args.pyproject)
    check_installed(args.installed_python, expected_version)

    print("All package verification checks passed.")


if __name__ == "__main__":
    main()
