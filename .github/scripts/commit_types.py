"""Shared Conventional Commit type list and exact-lowercase type check.

Single source of the allowed-type list and the type-casing rule, used by
both the local ``commit-msg`` git hook (via this module's own CLI entry
point below, wired up as its own hook in ``.pre-commit-config.yaml``) and
``.github/scripts/validate_commits.py`` (via direct import) -- see
``docs/development/commits.md#allowed-commit-types`` and
``docs/development/claude-code.md#commit-message-validation``.

This module deliberately does not implement Conventional Commits parsing in
general -- ``conventional-pre-commit`` already does that, both locally and
in CI. It only extracts and checks the casing of the commit type token, a
rule ``conventional-pre-commit`` does not itself enforce: empirically,
``Feat(config): add loader`` passes its default *and* ``--strict`` modes.
A message whose type is not one of ``ALLOWED_TYPES`` at all (wrong word, not
just wrong case) or that has no recognizable ``type:`` prefix in the first
place is intentionally left alone here -- ``conventional-pre-commit``
already rejects both cases on its own, with its own message.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Must match docs/development/commits.md#allowed-commit-types exactly, and
# stay in sync with the `entry:` args of the `conventional-pre-commit` hook
# in .pre-commit-config.yaml -- both restate this same list because YAML
# cannot import a Python constant, but this tuple is the one normative,
# importable source for every Python-side check.
ALLOWED_TYPES = (
    "feat",
    "fix",
    "docs",
    "refactor",
    "test",
    "chore",
    "perf",
    "style",
    "build",
    "ci",
    "revert",
)

# `type`, `type(scope)`, `type!`, or `type(scope)!`, immediately followed by
# `:`. Only the type token itself is captured; everything else in
# Conventional Commits syntax is left to conventional-pre-commit.
_TYPE_PATTERN = re.compile(r"^([A-Za-z]+)(?:\([^)]*\))?!?:")


def extract_type(subject: str) -> str | None:
    """Return the raw type token from a commit subject line, if present."""
    match = _TYPE_PATTERN.match(subject)
    return match.group(1) if match else None


def casing_error(subject: str) -> str | None:
    """Return a casing-error message, or None if there is no casing problem.

    Returns None both when the type is already an exact, valid lowercase
    match, and when the subject has no recognizable type prefix or an
    unrelated/unknown type -- those are not casing problems and are left to
    conventional-pre-commit's own validation.
    """
    raw_type = extract_type(subject)
    if raw_type is None or raw_type in ALLOWED_TYPES or raw_type.lower() not in ALLOWED_TYPES:
        return None
    return (
        f"commit type {raw_type!r} must be exact lowercase ({raw_type.lower()!r}), not {raw_type!r}"
    )


def main() -> None:
    """CLI entry point for the local `commit-msg` hook: check one message file."""
    msg_path = Path(sys.argv[1])
    lines = msg_path.read_text(encoding="utf-8").splitlines()
    subject = lines[0] if lines else ""

    error = casing_error(subject)
    if error is None:
        return

    print(f"[Bad commit message] >> {subject}", file=sys.stderr)
    print(f"FAIL: {error}", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
