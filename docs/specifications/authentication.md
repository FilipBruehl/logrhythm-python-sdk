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
status model in [Design Specifications](README.md). Several questions this
specification would normally answer are, deliberately, left open — see
[Open Questions](#open-questions).

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

This section describes the conceptual role of authentication information within the
SDK — not concrete fields, and not a Python class.

Authentication information is the credential material the SDK will eventually need
to prove identity to LogRhythm. Structurally, [SPEC-002](configuration.md) already
anticipates this: its
[Configuration Model](configuration.md#configuration-model) names
"Authentication-related inputs" as one of the groups a resolved `Configuration`
holds. `Authentication`, as described by this specification, **is** that group —
this specification does not introduce a second, separate place for authentication
information to live outside `Configuration`.

For version 1, that credential material is a bearer token (see
[Supported Authentication Types](#supported-authentication-types)). This
specification decides the mechanism, not the token's concrete representation within
`Authentication`/`Configuration` — that remains conceptual here, consistent with
[SPEC-002](configuration.md#configuration-model)'s own restraint from inventing field
names.

## Supported Authentication Types

**Decision: Bearer Token Authentication is the supported authentication mechanism
for version 1.** [Architecture Overview](../architecture/overview.md) already names
"bearer token authentication" twice, as a planned `core` responsibility; this
specification adopts that as a binding decision for its own scope — version 1 of the
SDK supports exactly one authentication mechanism, bearer token.

This decision covers only **which mechanism** the SDK supports. It does **not**
decide, and explicitly defers to a future Transport specification:

- how a bearer token is concretely attached to a request (e.g. as an `Authorization`
  header) — see [Non-Goals](#non-goals).
- the exact internal representation of the token value within
  `Authentication`/`Configuration` — see [Authentication Model](#authentication-model).

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
  ([SPEC-002](configuration.md#immutability-and-mutation)), the authentication
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
[SPEC-002, Integration with LogRhythmClient](configuration.md#integration-with-logrhythmclient)).

- **No ownership.** `LogRhythmClient` does not separately own authentication
  information; whatever ownership applies is `Configuration`'s, per
  [SPEC-002](configuration.md#integration-with-logrhythmclient).
- **No resources.** There is nothing here for `LogRhythmClient` to acquire or
  release.
- **No lifecycle responsibility.** `LogRhythmClient` has no lifecycle duty toward
  authentication information beyond what it already has toward `Configuration` as a
  whole (none — see [SPEC-002, No lifecycle resources](configuration.md#integration-with-logrhythmclient)).

## Secret Handling

- Authentication information must never be logged.
- Authentication information must never appear in `repr()` or any other default
  string representation.
- Authentication information must never appear in exceptions or error messages.
- Copies of authentication information must be kept to the minimum necessary.
- Authentication information must not be serialized unintentionally.

These follow directly from [SPEC-000](design-principles.md)'s security principles
and restate, for authentication information specifically, the same rules
[SPEC-002](configuration.md#secrets) already states for secrets held in
`Configuration` generally — this specification does not introduce a different or
additional rule. No decision about secret-manager integration is made here; see
[Future Extensions](#future-extensions-non-binding).

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

[SPEC-002](configuration.md#validation) names "future Authentication/Transport
specifications" as the eventual home for server-side validation of configuration
values. This specification clarifies that `Authentication`, as described here, is
**not** where that happens; if it happens anywhere, it belongs to a future Transport
(or equivalent) specification. This is a narrowing of an intentionally open forward
reference in SPEC-002, not a contradiction of it.

## Lifecycle

Authentication information has:

- no resources.
- no context manager.
- no cleanup logic.

Its lifecycle is entirely governed by `Configuration`'s — see
[Integration with Configuration](#integration-with-configuration) and
[SPEC-002](configuration.md#immutability-and-mutation).

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

Pseudocode only — illustrative of intended usage, not a committed API surface, not a
real implementation, and not a claim about the token's concrete representation.
Placeholder values only; no real credentials.

**Authentication information (a bearer token) as part of `Configuration`:**

```python
configuration = Configuration(
    connection=...,
    authentication=...,  # placeholder for the bearer token value (version 1's
    # decided mechanism); its exact internal representation is not decided here
    tls=...,
    logging=...,
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

These are explicitly undecided. They must not be resolved silently by
implementation; each requires an explicit decision (and, where architecturally
significant, an ADR) before it can move out of this list.

- **Credential typing.** Whether the bearer token is strictly typed (e.g. a
  dedicated wrapper type) or represented generically (e.g. a plain string) within
  `Authentication`/`Configuration` (see
  [Authentication Model](#authentication-model)).

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
