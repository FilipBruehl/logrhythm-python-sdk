# SPEC-003 — Authentication

| Field | Value |
| --- | --- |
| ID | SPEC-003 |
| Status | Accepted |
| Phase | A.2.4 |
| Component | Authentication |
| Depends on | [SPEC-000](design-principles.md), [SPEC-001](sdk-client.md), [SPEC-002](configuration.md) |
| Implementation | Not implemented |

## Status

Accepted — target architecture, not yet implemented. This specification has been
reviewed against the [Review Criteria](README.md#review-criteria) in
[Design Specifications](README.md) and is binding for implementation; see the
status model in [Design Specifications](README.md). The version 1 authentication
input is closed; future mechanisms remain non-binding.

## Purpose

`Authentication` represents exclusively the SDK's authentication information — for
version 1, a bearer token (see
[Supported Authentication Types](#supported-authentication-types)). It is
information, not behavior. The component:

- does not authenticate requests itself.
- has no network logic.
- performs no login flows.
- contains no HTTP implementation.

Actually attaching that information to a request (e.g. as a header) is the
responsibility of a future Transport specification, not this one. See
[Non-Goals](#non-goals).

## Scope

**In scope:**

- The role and responsibilities of authentication information within the SDK.
- Its conceptual representation (not concrete fields, not a Python class).
- That Bearer Token Authentication is the supported mechanism for version 1 (see
  [Supported Authentication Types](#supported-authentication-types)) — this
  specification decides only *which mechanism*, not its concrete transport-level
  implementation.
- How it integrates with [SPEC-002 — Configuration](configuration.md).
- How it integrates with [SPEC-001 — SDK Client](sdk-client.md).
- Secret handling requirements.
- The categories of (local-only) validation it may undergo.
- Its lifecycle (or lack thereof).
- Its testability requirements.

**Out of scope** (referenced only; defined by their own future specifications):

- HTTP headers (how a credential is actually placed on a request).
- TLS.
- Token refresh.
- OAuth flows.
- Session management.
- Concrete REST endpoints.
- Transport behavior.

## Responsibilities

Authentication information:

- represents the SDK's authentication information.
- is provided for later Transport components to use — it does not use itself.
- is handled securely wherever it exists, for as long as it exists (see
  [Secret Handling](#secret-handling)).
- integrates with [Configuration](configuration.md) (see
  [Integration with Configuration](#integration-with-configuration)).
- supports dependency injection: it can be constructed/supplied directly, without
  going through any network-backed or interactive source.
- is testable in isolation (see [Testability](#testability)).

## Non-Responsibilities

Authentication information:

- does not build HTTP requests.
- does not open connections.
- does not refresh tokens.
- does not perform logins.
- has no knowledge of REST endpoints.
- owns no resources.
- performs no network access.

## Authentication Model

This section describes the role of authentication information within the SDK.

Authentication information is the credential material the SDK will eventually need
to prove identity to LogRhythm. Structurally, [SPEC-002](configuration.md) already
anticipates this: its
[Configuration Schema](configuration.md#configuration-schema) names
"Authentication-related inputs" as one of the groups a resolved `Configuration`
holds. `Authentication`, as described by this specification, **is** that group —
this specification does not introduce a second, separate place for authentication
information to live outside `Configuration`.

For version 1, that credential material is the required
`logrhythm.authentication.bearer_token` field defined by
[SPEC-002](configuration.md#authentication). It uses Pydantic `SecretStr`; there is
no plain-string or separately owned credential representation.

## Supported Authentication Types

**Decision: Bearer Token Authentication is the supported authentication mechanism
for version 1.** [Architecture Overview](../architecture/overview.md) already names
"bearer token authentication" twice, as a planned `core` responsibility; this
specification adopts that as a binding decision for its own scope — version 1 of the
SDK supports exactly one authentication mechanism, bearer token.

This decision covers **which mechanism** the SDK supports. How a bearer token is
attached to a request (e.g. as an `Authorization` header) remains Transport's
responsibility — see [Non-Goals](#non-goals). The token's safe Configuration
representation is owned by [SPEC-002](configuration.md#authentication).

API Key, Basic Authentication, and Client Certificate Authentication are explicitly
**not** part of version 1. They remain possible future mechanisms — see
[Future Extensions](#future-extensions-non-binding) — and this specification decides
nothing further about them.

## Integration with Configuration

- `Configuration` (see [SPEC-002](configuration.md)) holds the authentication
  information — as its "Authentication-related inputs" group.
- `Authentication`, as described here, does not process, parse, or interpret that
  information itself; it is represented, not acted upon.
- Because a resolved `Configuration` is immutable
  ([SPEC-002](configuration.md#immutability-and-lifecycle)), the authentication
  information it holds is immutable for the same reason and by the same mechanism —
  this specification introduces no separate immutability rule of its own.
- **Decision: `Authentication` is not a standalone SDK object.** It is the
  authentication area within the immutable `Configuration` from
  [SPEC-002](configuration.md) — a group of fields, not a separately constructed or
  separately owned component. This specification does not introduce, and explicitly
  rules out, a second, independent `Authentication` type that would exist alongside
  `Configuration`.

## Integration with LogRhythmClient

`LogRhythmClient` (see [SPEC-001](sdk-client.md)) never receives authentication
information directly or independently. It obtains it only indirectly, as part of the
`Configuration` it is constructed with or resolves via `from_config(...)` (see
[SPEC-002, Public and Internal Interface](configuration.md#public-and-internal-interface)).

- **No ownership.** `LogRhythmClient` does not separately own authentication
  information; whatever ownership applies is `Configuration`'s, per
  [SPEC-002](configuration.md#public-and-internal-interface).
- **No resources.** There is nothing here for `LogRhythmClient` to acquire or
  release.
- **No lifecycle responsibility.** `LogRhythmClient` has no lifecycle duty toward
  authentication information beyond what it already has toward `Configuration` as a
  whole (none — see [SPEC-002, Immutability and Lifecycle](configuration.md#immutability-and-lifecycle)).

## Secret Handling

- Authentication information must never be logged.
- Authentication information must never appear in `repr()` or any other default
  string representation.
- Authentication information must never appear in exceptions or error messages.
- Authentication information must never remain reachable through structured error
  data, exception causes, or exception contexts.
- Copies of authentication information must be kept to the minimum necessary.
- Authentication information must not be serialized unintentionally.

These follow directly from [SPEC-000](design-principles.md)'s security principles
and restate, for authentication information specifically, the same rules
[SPEC-002](configuration.md#secret-safety) already states for secrets held in
`Configuration` generally — this specification does not introduce a different or
additional rule. No decision about secret-manager integration is made here; see
[Future Extensions](#future-extensions-non-binding).

Because `Configuration` contains this credential, its supported programmatic and
file-based construction paths apply the sanitized component boundary defined by
[SPEC-002](configuration.md#pydantic-validation-boundary). A raw, input-bearing
Pydantic or parser exception is internal validation detail and is never preserved as
a publicly reachable cause or context. `SecretStr` and hidden rendered Pydantic
inputs remain defense in depth, not the sole secret-safety mechanism.

## Validation

Only **local** validation is in scope:

- Syntactic and structural checks on the authentication information's shape (e.g.
  that a required value is present and non-empty), consistent with
  [SPEC-002](configuration.md#validation)'s syntactic/structural/semantic-local
  categories.
- **Fail fast:** invalid authentication information is rejected immediately, as part
  of `Configuration` resolution, not discovered later — per
  [SPEC-000](design-principles.md).

Explicitly **not** in scope:

- No server-side validation (whether a credential is actually accepted by
  LogRhythm).
- No login tests.
- No reachability checks.

[SPEC-002](configuration.md#validation) likewise excludes remote credential checks
from Configuration resolution. Credential acceptance is observable only through a
real request made later by Transport; Authentication defines no separate preflight
or server-validation step.

## Lifecycle

Authentication information has:

- no resources.
- no context manager.
- no cleanup logic.

Its lifecycle is entirely governed by `Configuration`'s — see
[Integration with Configuration](#integration-with-configuration) and
[SPEC-002](configuration.md#immutability-and-lifecycle).

## Testability

- Authentication information must be fully testable offline — no network
  dependencies of any kind.
- Tests must use placeholder values only; no real credentials, in this
  specification or in any test.
- Because authentication information is represented within an immutable
  `Configuration` (see [Integration with Configuration](#integration-with-configuration)),
  it can be constructed once per test and reused without risk of mutation between
  assertions, consistent with [SPEC-002](configuration.md#testability).

## Examples

Pseudocode only — illustrative of intended usage, not a class signature or real
implementation. Placeholder values only; no real credentials.

**Authentication information (a bearer token) as part of `Configuration`:**

```python
configuration = Configuration(
    logrhythm={
        "base_url": "https://example.invalid",
        "port": 8501,
        "authentication": {"bearer_token": "placeholder-token"},
    }
)
```

**Flowing into `LogRhythmClient` indirectly, via `Configuration`:**

```python
client = LogRhythmClient(configuration)
# `configuration` carries the bearer token. LogRhythmClient does not process it
# directly, and neither does Authentication itself — a future Transport component
# will eventually be the one that attaches it to a request.
```

## Open Questions

There are no remaining open questions for the version 1 authentication input. The
previous credential-typing question is closed by SPEC-002's `SecretStr` decision.

## Future Extensions (non-binding)

These are possible ideas for later, explicitly non-binding, and do not represent any
architectural decision or part of SPEC-003:

- API Key Authentication (not part of version 1; see
  [Supported Authentication Types](#supported-authentication-types)).
- Basic Authentication (not part of version 1; see
  [Supported Authentication Types](#supported-authentication-types)).
- Client Certificate Authentication (not part of version 1; see
  [Supported Authentication Types](#supported-authentication-types)).
- OAuth.
- Token refresh.
- Single sign-on (SSO).
- Hardware-backed secrets.
- Secret manager integration.
- Multi-factor authentication.

## Non-Goals

This specification, and by extension `Authentication` itself, explicitly does not
cover:

- HTTP.
- TLS.
- Session management.
- Transport.
- Login.
- Retry.
- Token refresh.
- OAuth flows.
- Remote authentication.

## References

- [SPEC-000 — Design Principles](design-principles.md)
- [SPEC-001 — SDK Client](sdk-client.md)
- [SPEC-002 — Configuration](configuration.md)
- [Architecture Overview](../architecture/overview.md)
- [Component Model](../architecture/components.md)
- No existing ADR (see [docs/adr/](../adr/README.md)) is specific to authentication
  architecture; none is referenced here as directly applicable.
