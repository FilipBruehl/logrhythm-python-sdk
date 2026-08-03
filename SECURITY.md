# Security Policy

## Reporting a vulnerability

If you believe you have found a security vulnerability in `logrhythm-python-sdk`,
please report it privately rather than opening a public GitHub issue.

**Preferred path — report privately:**

- Contact a repository maintainer directly through a private channel, if one is
  available to you.
- If no private channel is available, open a GitHub issue that states only that
  you have a security concern to disclose — **without** any technical detail,
  proof-of-concept code, logs, tokens, or credentials — and a maintainer will
  follow up through a private channel to gather further details.

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
