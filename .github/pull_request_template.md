# Pull Request

<!--
  One shared template for every PR — feature, fix, or documentation-only.
  This template is a helper, not a normative source: if anything here ever
  conflicts with a SPEC, an ADR, or a workflow document under
  docs/development/, that document wins — see
  docs/development/templates.md#template-governance.
-->

## Summary

<!-- What changed, why it was necessary, and what result this achieves.
     Keep this short and non-technical — the "Changes" section below is
     where the technical detail goes. -->

## Scope

<!-- Which resource/component/document this PR touches, and what is
     explicitly out of scope. See docs/development/definition-of-ready.md. -->

## Architecture and Specifications

<!-- Which SPEC(s) and/or ADR(s) this change implements or is governed by.
     If none apply, say so explicitly. See
     docs/development/pull-requests.md#required-pr-content and
     docs/adr/README.md#when-an-adr-is-required. -->

## Changes

<!-- The technical detail: what was actually changed, file by file or
     concern by concern, for a reviewer who needs to understand the diff. -->

## Testing and Quality Checks

<!-- What was tested and how: new tests added, existing tests still passing,
     manual verification performed. Quality-check results belong in the
     Checklist below. -->

## Security Considerations

<!-- Secrets, credentials, TLS/redaction defaults, or other security-relevant
     behavior this change touches — or an explicit "none" if it doesn't. -->

## Public API and Compatibility

<!-- Any new or changed public export, client method, model, or exception.
     Flag explicitly if this is a breaking change. "None" if not applicable. -->

## Documentation

<!-- Which docs were updated in the same change, or why none were needed. -->

## Checklist

- [ ] Scope kept as stated above — no unrelated drive-by changes
- [ ] Relevant SPECs checked
- [ ] Relevant ADRs checked
- [ ] Tests added, or their absence justified
- [ ] Local quality check successful (`uv run pre-commit run --all-files`)
- [ ] `pytest` successful
- [ ] Documentation updated
- [ ] No secrets in code, tests, docs, or commit messages
- [ ] Breaking changes called out above (or none)
- [ ] API Coverage Matrix updated (if this touches a documented endpoint)
- [ ] Target branch is correct (see `docs/development/branching.md`)
- [ ] Commit history is preserved — no squash requested

## Open Points

<!-- Anything still undecided, deferred, or worth a reviewer's attention. -->
