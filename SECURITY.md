# Security Policy

## Reporting a vulnerability

If you believe you have found a security vulnerability in `logrhythm-python-sdk`,
do not open a public GitHub issue or disclose vulnerability details publicly.

The intended private reporting path is GitHub Private Vulnerability Reporting:
open the repository's **Security** area, select **Report a vulnerability**, and
submit the report there. The repository owner must manually enable this feature
under **Settings → Security → Private vulnerability reporting**; repository
files and workflows do not activate it.

If **Report a vulnerability** is not available, do not put technical details,
proof-of-concept code, logs, tokens, or credentials in a public issue. Use only
an existing nontechnical, organizationally appropriate contact path to ask the
repository owner or a maintainer to establish a private channel. Do not include
the vulnerability itself in that request.

The vulnerability itself is never discussed in public issue comments, pull
requests, or commit messages before it has been assessed and, where applicable,
fixed.

## Do not post real credentials

**Never include real bearer tokens, API keys, passwords, or other live credentials**
in an issue, pull request, commit, log excerpt, or any other content submitted to
this repository — including when reporting a bug or security issue. If a credential
has been exposed, revoke or rotate it immediately regardless of where it was posted.

## Scope

This project is an SDK (a client library), not a hosted service. Vulnerabilities in
LogRhythm's own products or APIs are out of scope for this repository and should be
reported to LogRhythm directly through their own security process.

## Supported versions

This project is in an early, pre-1.0 development stage. Until a first stable release
is published, only the latest released version is supported with security fixes.
