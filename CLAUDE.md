# Claude Code Adapter

## Purpose

This file adapts Claude Code to this repository. All project-wide AI
Development governance is defined exclusively in [AGENTS.md](AGENTS.md), which
must be read and followed before work begins.

This adapter does not repeat or override those rules.

## Claude Code-specific integration

- Versioned project permissions live in [`.claude/settings.json`](.claude/settings.json).
- Machine-local permissions may live in `.claude/settings.local.json`; that file
  is ignored and must not be committed or edited on the user's behalf.
- The project settings use Claude Code's `allow`, `ask`, and `deny` permission
  rules. A technical `allow` never grants content authority that AGENTS.md or
  the user's request does not grant.
- Destructive Git operations, hook bypasses, force pushes, and likely
  secret-bearing files are denied by project settings where Claude Code's
  matcher can express the restriction.
- Commands not covered by a project permission may still require an interactive
  Claude Code approval.

Technical details of the settings file are documented in
[Claude Code: Technical Settings](docs/development/claude-code.md).
