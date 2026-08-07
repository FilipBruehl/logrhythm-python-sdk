# API Coverage Matrix

> **Status of this document:** structure only. The official LogRhythm API surface has
> not been inventoried yet, so this page defines the matrix that will later track
> coverage — it does not list real endpoints. No endpoint, model, or resource name
> below is invented; see
> [API Implementation Workflow](../development/api-implementation-workflow.md) for how
> rows get populated with real data once an API area is actually inventoried.

## Purpose

Give one place to see, per LogRhythm API area, how far the SDK has progressed from
"not looked at yet" to "implemented, tested, and documented." Each row will
eventually correspond to one real, documented endpoint or a closely related group of
endpoints.

## Columns

| Column | Meaning |
| --- | --- |
| API | The LogRhythm API area (Administration, AI Engine Cache Drilldown, Metrics, AI Engine, Alarm, Case, or Search — see [SPEC-010, Supported APIs](../specifications/api-modules.md#supported-apis)). |
| Area | A sub-area or resource group within that API, once known (e.g. a resource category). |
| Endpoint | The specific documented endpoint (method + path), once inventoried. |
| Specification | Link to the compressed Markdown implementation spec for this endpoint (see [API Implementation Workflow](../development/api-implementation-workflow.md), step 3), once written. |
| Models | Whether the typed models for this endpoint's request/response exist. |
| Implementation | Whether the client/resource implementation exists. |
| Tests | Whether unit tests with mocked HTTP calls exist for this endpoint. |
| Documentation | Whether user-facing documentation for this endpoint exists. |
| Status | One of the status values below. |
| Notes | Known gaps, ambiguities in vendor documentation, or other caveats — never a guess used to fill a gap. |

## Status values

| Status | Meaning |
| --- | --- |
| `Not inventoried` | The endpoint has not yet been catalogued from official documentation. |
| `Planned` | Catalogued and intended for implementation, not yet started. |
| `Specification ready` | An `Accepted` Design Specification exists for this endpoint. |
| `In progress` | Implementation has started but is not complete. |
| `Partial` | Implemented for some but not all documented cases (e.g. missing optional parameters or response variants). |
| `Implemented` | Implementation and tests exist and match the specification. |
| `Verified` | Implemented and additionally confirmed against a real or sanctioned LogRhythm environment. |
| `Blocked` | Cannot proceed — for example, official documentation is missing, contradictory, or access to verify behavior is unavailable. |
| `Not supported` | Deliberately out of scope for the SDK, with the reason captured in Notes. |

## Coverage matrix

No endpoints have been inventoried yet for any API area. One placeholder row per
planned API area is listed below; each will be expanded into real rows once that
area's official documentation has been catalogued per
[API Implementation Workflow](../development/api-implementation-workflow.md).

| API | Area | Endpoint | Specification | Models | Implementation | Tests | Documentation | Status | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Administration API | – | – | – | – | – | – | – | Not inventoried | Awaiting official documentation inventory. |
| AI Engine Cache Drilldown API | – | – | – | – | – | – | – | Not inventoried | Awaiting official documentation inventory. |
| Metrics API | – | – | – | – | – | – | – | Not inventoried | Awaiting official documentation inventory. |
| AI Engine API | – | – | – | – | – | – | – | Not inventoried | Awaiting official documentation inventory. |
| Alarm API | – | – | – | – | – | – | – | Not inventoried | Awaiting official documentation inventory. |
| Case API | – | – | – | – | – | – | – | Not inventoried | Awaiting official documentation inventory. |
| Search API | – | – | – | – | – | – | – | Not inventoried | Awaiting official documentation inventory. |
