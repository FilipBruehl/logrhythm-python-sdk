"""Validate commit messages in a push or pull-request range.

CI-only helper for the ``commit-message`` job (see
``.github/workflows/ci.yml`` and
``docs/development/ci.md#commit-message-job``). Not part of the published
SDK and never imported by it. Uses the standard library plus the project's
own ``conventional-pre-commit`` dev dependency -- invoked through its
published console-script entry point (never an internal, unstable module
API), so this script validates with exactly the same tool, version, and
allowed-type list as the local ``commit-msg`` hook in
``.pre-commit-config.yaml``. The commit type's exact lowercase casing --
which ``conventional-pre-commit`` does not itself enforce -- is checked via
``commit_types.casing_error``, the same shared, single-source
implementation the local ``commit-type-lowercase`` hook uses.

Special cases -- all empirically verified against the tool's actual,
non-strict behavior; see
``docs/development/claude-code.md#commit-message-validation`` for the test
transcript this relies on:

- A merge commit (two or more parents) is skipped, not validated -- it is
  either a deliberate merge-commit-strategy PR merge or a GitHub-generated
  merge, never hand-written Conventional Commits prose.
- A ``fixup!``/``squash!`` commit is rejected outright. The tool accepts
  these without ``--strict``, but they must never remain in a range that is
  about to land on ``main``/``integration/**``.
- Git's own default revert subject (``Revert "<original subject>"``) is
  accepted as a recognized exception -- the tool rejects this exact format
  even without ``--strict``.
- Every other commit is validated with the tool's default (non-strict) mode.
  ``--strict`` is deliberately not used: it would reject merge and
  ``fixup!``/``squash!`` commits outright rather than letting this script
  tell them apart with its own, more specific handling above.

Nothing here modifies the repository; git is used read-only throughout.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

from commit_types import ALLOWED_TYPES, casing_error

# Git's sentinel `before` SHA for a push that created a new branch/ref -- see
# docs/development/ci.md#ci-commit-range.
ZERO_SHA = "0000000000000000000000000000000000000000"


def fail(message: str) -> None:
    """Print a failure message to stderr and exit non-zero."""
    print(f"FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def ok(message: str) -> None:
    """Print a success message to stdout."""
    print(f"OK: {message}")


def _git(*args: str) -> str:
    """Run a read-only git command and return its stripped stdout."""
    result = subprocess.run(["git", *args], capture_output=True, text=True, check=True)
    return result.stdout.strip()


def commit_range(base: str, head: str) -> list[str]:
    """Return commit SHAs introduced by `head` since `base`, oldest first.

    Falls back to validating `head` alone when `base` is empty or the
    all-zeros sentinel -- a new branch's first push, or a manual
    `workflow_dispatch` run, has no meaningful base and this is the
    documented, non-silent fallback for that case. An explicit, non-fallback
    range that resolves to zero commits is treated as an error instead of a
    silent pass.
    """
    if not base or base in (ZERO_SHA, head):
        return [head]
    output = _git("rev-list", "--first-parent", "--reverse", f"{base}..{head}")
    shas = [line for line in output.splitlines() if line]
    if not shas:
        fail(
            f"commit range {base}..{head} contains no commits to validate -- "
            "refusing to silently treat an empty range as a pass"
        )
    return shas


def is_merge_commit(sha: str) -> bool:
    """Return True if `sha` has two or more parents."""
    parents = _git("log", "-1", "--format=%P", sha).split()
    return len(parents) >= 2


def commit_subject(sha: str) -> str:
    """Return the first line of `sha`'s commit message."""
    return _git("log", "-1", "--format=%s", sha)


def commit_message(sha: str) -> str:
    """Return the full commit message of `sha`."""
    return _git("log", "-1", "--format=%B", sha)


def is_git_default_revert(subject: str) -> bool:
    """Return True for git's own default revert subject: `Revert "<subject>"`."""
    return subject.startswith('Revert "') and subject.endswith('"')


def is_fixup_or_squash(subject: str) -> bool:
    """Return True for a `fixup!`/`squash!` autosquash commit subject."""
    return subject.startswith("fixup!") or subject.startswith("squash!")


def find_conventional_pre_commit() -> Path:
    """Locate the console script installed next to the current interpreter."""
    suffix = ".exe" if sys.platform == "win32" else ""
    candidate = Path(sys.executable).with_name(f"conventional-pre-commit{suffix}")
    if not candidate.is_file():
        fail(
            f"conventional-pre-commit console script not found next to {sys.executable} "
            "-- run this script via `uv run python .github/scripts/validate_commits.py`"
        )
    return candidate


def validate_with_tool(message: str, conventional_pre_commit: Path) -> tuple[bool, str]:
    """Run the installed conventional-pre-commit console script against `message`.

    The message is written to a temporary file and passed as a file-path
    argument, never interpolated into a shell command string, so nothing
    about a commit's own (untrusted) content is ever assembled into shell
    syntax.
    """
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as handle:
        handle.write(message)
        msg_path = Path(handle.name)
    try:
        result = subprocess.run(
            [str(conventional_pre_commit), *ALLOWED_TYPES, str(msg_path)],
            capture_output=True,
            text=True,
            check=False,
        )
    finally:
        msg_path.unlink(missing_ok=True)
    return result.returncode == 0, (result.stdout + result.stderr).strip()


def main() -> None:
    """Validate every commit in the requested range, reporting all failures."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base", default="", help="Base SHA (exclusive); empty for the single-commit fallback."
    )
    parser.add_argument("--head", required=True, help="Head SHA (inclusive).")
    args = parser.parse_args()

    conventional_pre_commit = find_conventional_pre_commit()
    shas = commit_range(args.base, args.head)

    failures: list[str] = []
    for sha in shas:
        subject = commit_subject(sha)
        short = sha[:12]

        if is_merge_commit(sha):
            ok(f"{short} skipped (merge commit): {subject!r}")
            continue

        if is_fixup_or_squash(subject):
            failures.append(
                f"{short} is a fixup!/squash! commit and must not remain in this range: {subject!r}"
            )
            continue

        if is_git_default_revert(subject):
            ok(f"{short} accepted (git default revert message): {subject!r}")
            continue

        casing_problem = casing_error(subject)
        if casing_problem is not None:
            failures.append(f"{short} {casing_problem}: {subject!r}")
            continue

        valid, output = validate_with_tool(commit_message(sha), conventional_pre_commit)
        if valid:
            ok(f"{short} valid: {subject!r}")
        else:
            failures.append(f"{short} invalid: {subject!r}\n{output}")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        sys.exit(1)

    print(f"All {len(shas)} commit message(s) valid.")


if __name__ == "__main__":
    main()
