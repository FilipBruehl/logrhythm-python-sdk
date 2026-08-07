"""Validate release version sources and extract curated release notes.

The release workflow uses this standard-library-only helper before building or
publishing. It validates the tag, ``pyproject.toml``, ``uv version``, the
package ``__version__`` mirror, and the matching ``CHANGELOG.md`` section.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import NoReturn

VERSION_PATTERN = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:(a|b|rc)(0|[1-9]\d*))?$"
)


def fail(message: str) -> NoReturn:
    """Print a release-validation failure and exit non-zero."""
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def ok(message: str) -> None:
    """Print a successful release-validation result."""
    print(f"OK: {message}")


def read_project_version(pyproject_path: Path) -> str:
    """Read the canonical project version from ``pyproject.toml``."""
    with pyproject_path.open("rb") as handle:
        pyproject = tomllib.load(handle)
    version = pyproject.get("project", {}).get("version")
    if not isinstance(version, str):
        fail(f"missing string project.version in {pyproject_path}")
    return version


def read_package_version(package_path: Path) -> str:
    """Read the package's static ``__version__`` mirror."""
    content = package_path.read_text(encoding="utf-8")
    match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']\s*$', content, re.MULTILINE)
    if match is None:
        fail(f"could not find a static __version__ assignment in {package_path}")
    return match.group(1)


def read_uv_version() -> str:
    """Read the project version through uv's supported version command."""
    result = subprocess.run(
        ["uv", "version", "--short"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        fail(f"uv version --short failed:\n{result.stdout}{result.stderr}")
    return result.stdout.strip()


def extract_release_notes(changelog_path: Path, version: str, tag: str) -> str:
    """Return the curated changelog section for ``version`` as release notes."""
    content = changelog_path.read_text(encoding="utf-8")
    heading_pattern = re.compile(
        rf"^## \[{re.escape(version)}\] - (?P<date>\d{{4}}-\d{{2}}-\d{{2}})\s*$",
        re.MULTILINE,
    )
    headings = list(heading_pattern.finditer(content))
    if not headings:
        fail(f"{changelog_path} has no dated section for version {version}")
    if len(headings) != 1:
        fail(
            f"{changelog_path} contains {len(headings)} dated sections for version "
            f"{version}; exactly one is expected"
        )
    heading = headings[0]
    try:
        dt.date.fromisoformat(heading.group("date"))
    except ValueError:
        fail(f"invalid ISO release date for version {version} in {changelog_path}")

    following = content[heading.end() :]
    next_boundary = re.search(r"^(?:## \[|\[[^\]]+\]:\s)", following, re.MULTILINE)
    body = following[: next_boundary.start()] if next_boundary else following
    body = body.strip()
    if not re.search(r"^- \S", body, re.MULTILINE):
        fail(f"changelog section for version {version} contains no release entry")
    return f"# {tag}\n\n{body}\n"


def main() -> None:
    """Validate all release version sources and optionally write release notes."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", required=True, help="Release tag in v<version> format.")
    parser.add_argument("--pyproject", type=Path, default=Path("pyproject.toml"))
    parser.add_argument(
        "--package-init",
        type=Path,
        default=Path("src/logrhythm_sdk/__init__.py"),
    )
    parser.add_argument("--changelog", type=Path, default=Path("CHANGELOG.md"))
    parser.add_argument("--notes-output", type=Path)
    args = parser.parse_args()

    if not args.tag.startswith("v"):
        fail(f"tag must start with 'v': {args.tag!r}")
    tag_version = args.tag.removeprefix("v")
    if VERSION_PATTERN.fullmatch(tag_version) is None:
        fail(
            "tag version must use MAJOR.MINOR.PATCH with an optional PEP 440 "
            f"aN, bN, or rcN suffix: {args.tag!r}"
        )
    ok(f"tag format is valid: {args.tag}")

    project_version = read_project_version(args.pyproject)
    uv_version = read_uv_version()
    package_version = read_package_version(args.package_init)
    versions = {
        "tag": tag_version,
        "pyproject.toml": project_version,
        "uv version": uv_version,
        "__version__": package_version,
    }
    if len(set(versions.values())) != 1:
        fail(
            "release versions differ: "
            + ", ".join(f"{name}={value}" for name, value in versions.items())
        )
    ok(f"tag, pyproject.toml, uv version, and __version__ agree on {project_version}")

    notes = extract_release_notes(args.changelog, project_version, args.tag)
    ok(f"CHANGELOG.md contains a dated, non-empty {project_version} section")

    if args.notes_output is not None:
        args.notes_output.write_text(notes, encoding="utf-8")
        ok(f"wrote curated release notes to {args.notes_output}")

    print("All release validation checks passed.")


if __name__ == "__main__":
    main()
