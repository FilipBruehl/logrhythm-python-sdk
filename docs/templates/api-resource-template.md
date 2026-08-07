# Resource: \<Resource Name\>

<!--
  Template only — describes one whole business resource (e.g. "hosts"), not
  a single endpoint. For planning a single endpoint before this level of
  detail exists, use an API Endpoint issue instead — see
  docs/development/templates.md#available-templates. This template is a
  helper for step 3 ("Create a compressed Markdown implementation spec") of
  docs/development/api-implementation-workflow.md, not a replacement for any
  step in it, and never a substitute for the actual SPECs, ADRs, vendor
  documentation, the API Coverage Matrix, or tests — see
  docs/development/templates.md#template-governance.
-->

## API

<!-- Which of the seven vendor API areas this resource belongs to (see
     SPEC-010, Supported APIs), e.g. "Administration API". -->

## Resource

<!-- The business resource name, e.g. "hosts", and one or two sentences on
     what it represents. -->

## Package path

<!-- Where this resource lives on disk, per SPEC-010's Resource Hierarchy,
     e.g. `admin/hosts/`. -->

## Endpoints

<!-- One entry per documented endpoint this resource covers: HTTP method,
     relative path, and the planned SDK method name (see SPEC-010, Endpoint
     Methods). Add a row to docs/coverage/api-coverage.md for each. -->

| Method | Path | SDK method | Status |
| --- | --- | --- | --- |
| <!-- GET --> | <!-- /path --> | <!-- hosts.list --> | <!-- Not inventoried --> |

## Models

<!-- Request, response, and any resource-specific internal models this
     resource needs — see SPEC-008. Note which are Create/Update/Delete
     variants and why, per SPEC-008's Create/Update/Delete guidance. -->

## Filters

<!-- Resource-specific filter fields, per SPEC-009. "None documented" is a
     valid answer. -->

## Pagination

<!-- Whether this resource uses the shared, `core`-level pagination model
     (the default per SPEC-009/SPEC-010) or documents a genuinely different
     mechanism requiring its own model under this resource's `models/` — see
     SPEC-010, Resource Hierarchy. -->

## Sorting

<!-- Documented sortable fields, modeled as a resource-specific enum per
     SPEC-009. "None documented" is a valid answer. -->

## Options

<!-- Resource-specific functional options (e.g. `include`, `expand`), per
     SPEC-009's Functional Options — only where a documented need exists. -->

## Exceptions

<!-- Any resource-specific exception subclasses beyond the minimum set in
     SPEC-007, and why they are needed (see SPEC-007, Open Questions,
     "Additional API-specific exception subclasses"). "None beyond the
     minimum set" is a valid answer. -->

## Logging

<!-- Domain-level events this resource logs that `Transport` cannot know
     about, per SPEC-006/SPEC-010's logging-responsibility split. Confirm
     nothing here duplicates what `Transport` already logs. -->

## Tests

<!-- The test strategy for this resource: documentation-based,
     example-based, and/or verified integration tests, per SPEC-010,
     Testing. Note any fixtures and confirm they use only documented fields. -->

## Documentation sources

<!-- Which official LogRhythm documentation page(s) this resource is based
     on, including version/date if available — step 1 of
     docs/development/api-implementation-workflow.md. -->

## Coverage

<!-- Current docs/coverage/api-coverage.md status for this resource's
     endpoints, and a link to the relevant matrix rows. -->

## Open Questions

<!-- Anything ambiguous, undocumented, or still undecided for this resource
     — never filled in with a guess, per SPEC-000's "No invented API
     functionality" principle. -->
