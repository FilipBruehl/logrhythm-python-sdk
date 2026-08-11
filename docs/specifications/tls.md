# SPEC-004 — TLS

| Field | Value |
| --- | --- |
| ID | SPEC-004 |
| Status | Accepted |
| Phase | A.2.5 |
| Component | TLS |
| Depends on | [SPEC-000](design-principles.md), [SPEC-001](sdk-client.md), [SPEC-002](configuration.md) |
| Implementation | Not implemented |

## Status

Accepted — target architecture, not yet implemented. This specification has been
reviewed against the [Review Criteria](README.md#review-criteria) in
[Design Specifications](README.md) and is binding for implementation; see the
status model in [Design Specifications](README.md). A small number of questions
this specification would normally answer are, deliberately, left open — see
[Open Questions](#open-questions).

## Purpose

`TLS` represents the SDK's TLS-related security configuration — whether and how
certificates and hostnames are verified, and where trust comes from. It is
configuration, not behavior. The component:

- does not perform a TLS handshake itself.
- has no network logic.
- implements no cryptography.
- contains no HTTP or transport implementation.

Actually establishing a TLS connection using this configuration is the
responsibility of a future Transport specification, not this one. See
[Non-Goals](#non-goals).

## Scope

**In scope:**

- The role and responsibilities of TLS-related configuration within the SDK.
- Its conceptual representation (not concrete fields, not a Python class).
- Secure defaults for certificate and hostname verification.
- The explicit, non-default insecure (verification opt-out) mode and its
  constraints.
- Trust store behavior (system default vs. custom CA bundle).
- Accepted path types for a custom CA bundle, and how relative paths resolve.
- The minimum TLS version floor for version 1.
- What is explicitly out of version 1 (mTLS, client certificates, certificate
  pinning, OCSP, CRL).
- How it integrates with [SPEC-002 — Configuration](configuration.md).
- How it integrates with [SPEC-001 — SDK Client](sdk-client.md).
- The categories of (local-only) validation it may undergo.
- Its testability requirements.

**Out of scope** (referenced only; defined by their own future specifications, or
explicitly deferred — see [Non-Goals](#non-goals) and
[Future Extensions](#future-extensions-non-binding)):

- HTTP.
- Concrete HTTP client libraries.
- Transport implementation.
- Cryptography implementation.
- Certificate acquisition or renewal.
- OCSP.
- CRL.
- Certificate pinning.
- The SDK's exception hierarchy (exact exception class names/types).

## Responsibilities

TLS-related configuration:

- represents the SDK's TLS settings: verification mode, trust source, and minimum
  TLS version floor.
- reflects secure defaults correctly (see [Secure Defaults](#secure-defaults)) —
  representation only; actual enforcement happens when a future Transport
  specification establishes a connection.
- provides consistent, locally validated values to
  [Configuration](configuration.md) (see [Validation](#validation)).
- undergoes only local validation of any custom CA bundle path it holds (existence,
  readability) — never network or certificate-content validation (see
  [Validation](#validation)).
- supports dependency injection and testing: it can be constructed/supplied
  directly, without any real certificate or network dependency (see
  [Testability](#testability)).

## Non-Responsibilities

TLS-related configuration:

- does not perform a TLS handshake.
- does not implement HTTP.
- does not implement transport.
- does not implement cryptography.
- does not fetch or renew certificates.
- does not perform OCSP or CRL checks.
- does not pin certificates.
- owns no resources.
- performs no network access.

## TLS Model

This section describes the conceptual role of TLS-related configuration within the
SDK — not concrete fields, and not a Python class.

**Decision: `TLS` is not a standalone SDK object.** It is the TLS area within the
immutable `Configuration` from [SPEC-002](configuration.md) — a group of related
settings, not a separately constructed or separately owned component. This
specification does not introduce, and explicitly rules out, a second, independent
`TLS` type that would exist alongside `Configuration`.

Conceptually, the TLS area covers:

- a verification mode (secure — the default — or the explicit insecure opt-out; see
  [Secure Defaults](#secure-defaults) and
  [Certificate Verification](#certificate-verification)).
- a trust source (the platform/HTTP-library default trust store, or an optional
  custom CA bundle; see [Trust Store](#trust-store)).
- a minimum TLS version floor (see [Secure Defaults](#secure-defaults); this does
  *not* extend to cipher suite selection, which this specification does not
  prescribe).

No concrete field names, types, or a Python class are defined here — consistent with
[SPEC-002](configuration.md#configuration-model)'s own restraint from inventing field
names for the groups it anticipates.

## Secure Defaults

The following are binding architectural decisions, not open questions:

- **Certificate verification is enabled by default.**
- **Hostname verification is enabled by default.**
- **Insecure connections are never the default.** Choosing an insecure mode is
  always an explicit, deliberate act by the caller — never the outcome of an
  omitted or default setting.
- **Security-relevant defaults must be documented.** No implicit, undocumented TLS
  default exists.

These follow directly from [SPEC-000](design-principles.md)'s "TLS verification on
by default" and "Prefer secure defaults" principles, and from
[Architecture Overview](../architecture/overview.md), which already names this same
default. [SPEC-002](configuration.md#defaults) already cites this exact default as
its one already-decided concrete default value; this specification does not
re-decide it, only elaborates it for TLS specifically.

**Minimum TLS version.** Version 1 requires at least TLS 1.2, and uses TLS 1.3
where both the platform and the server support it. This specification does **not**
prescribe cipher suites of its own — no specific cipher suite list is defined here.
Whether the minimum version becomes configurable in the future is an
[Open Question](#open-questions); the floor itself (at least TLS 1.2) is not.

## Certificate Verification

Certificate verification is enabled by default (see
[Secure Defaults](#secure-defaults)). This specification defines only the
architectural shape of that decision, not the verification algorithm itself, which
belongs to a future Transport specification (see [Non-Goals](#non-goals)).
The endpoint-scheme policy is a separate concern governed by
[ADR-0008](../adr/0008-require-https-for-sdk-managed-endpoints.md); disabling
verification does not permit plain HTTP.

**An insecure mode — explicit opt-out of certificate verification — is permitted,**
under firm constraints that are binding, not open questions:

- It **must be explicitly enabled** by the caller. It is never enabled implicitly,
  as a side effect of an omitted, malformed, or otherwise unspecified setting.
- It **must produce a clear warning** at client creation or transport
  initialization — the caller is never left unaware that verification is disabled.
- That warning **must never contain secrets or target URLs**, consistent with
  [SPEC-000](design-principles.md)'s secret-handling principles ("Secrets are never
  logged", "Secrets are never exposed via `repr()`").
- It is intended **exclusively for exceptional cases** (for example, test or lab
  environments) — not as a normal or recommended operating mode. See
  [SPEC-000](design-principles.md#security-principles), "Security by default."

Whether the insecure mode needs safeguards beyond this warning is an
[Open Question](#open-questions).

## Hostname Verification

Hostname verification is enabled by default (see
[Secure Defaults](#secure-defaults)), alongside certificate verification. It
conceptually confirms that the presented certificate matches the host the SDK is
connecting to — the specific matching algorithm (e.g. handling of wildcard names) is
implementation detail belonging to a future Transport specification, not decided
here (see [Non-Goals](#non-goals)).

Hostname verification is governed by the same single insecure-mode opt-out described
under [Certificate Verification](#certificate-verification), not by an independent
toggle of its own — [Architecture Overview](../architecture/overview.md) describes
one unified opt-out ("explicit, deliberate opt-out of verification"), not separate
switches for certificate and hostname checks, and this specification does not invent
one.

## Trust Store

Version 1 bindingly supports exactly two trust sources:

1. **The platform's, or the future HTTP library's, default (system) trust store.**
   This is the default when no custom CA bundle is supplied.
2. **An optional custom CA bundle path.** When supplied, it **replaces** the system
   trust store entirely — the two are not merged or combined.

**Self-signed certificates** should be accommodated by supplying a custom CA bundle
that includes them (option 2 above) — **not** by disabling certificate verification.
Using the insecure mode (see [Certificate Verification](#certificate-verification))
to work around a self-signed certificate is explicitly discouraged by this
specification.

**Accepted path types.** Conceptually, a custom CA bundle path is accepted as
either a `str` or a `pathlib.Path` — no other representation is defined. Relative
paths are permitted and are resolved relative to the current working directory.
Which concrete file format(s) the bundle itself may contain (e.g. whether only PEM
is supported) is an [Open Question](#open-questions).

## Configuration Integration

- [Configuration](configuration.md) (see [SPEC-002](configuration.md)) holds the
  TLS-related information — as its "TLS-related inputs" group (see
  [SPEC-002, Configuration Model](configuration.md#configuration-model)).
- `TLS`, as described here, does not process or act on that information itself; it
  is represented, not enforced (see [TLS Model](#tls-model)).
- Because a resolved `Configuration` is immutable
  ([SPEC-002](configuration.md#immutability-and-mutation)), the TLS-related
  information it holds is immutable for the same reason and by the same
  mechanism — this specification introduces no separate immutability rule of its
  own.
- Local validation of TLS-related input (see [Validation](#validation)) happens as
  part of `Configuration` resolution, consistent with
  [SPEC-002](configuration.md#validation) — not earlier, and not deferred to later
  use.

## Integration with LogRhythmClient

`LogRhythmClient` (see [SPEC-001](sdk-client.md)) never receives TLS-related
configuration directly or independently. It obtains it only indirectly, as part of
the `Configuration` it is constructed with or resolves via `from_config(...)` (see
[SPEC-002, Integration with LogRhythmClient](configuration.md#integration-with-logrhythmclient)).

- **No ownership.** `LogRhythmClient` does not separately own TLS-related
  configuration; whatever ownership applies is `Configuration`'s, per
  [SPEC-002](configuration.md#integration-with-logrhythmclient).
- **No resources.** There is nothing here for `LogRhythmClient` to acquire or
  release.
- **No lifecycle responsibility.** `LogRhythmClient` has no lifecycle duty toward
  TLS-related configuration beyond what it already has toward `Configuration` as a
  whole (none — see
  [SPEC-002, No lifecycle resources](configuration.md#integration-with-logrhythmclient)).

## Validation

Only **local** validation is in scope, consistent with
[SPEC-002](configuration.md#validation)'s syntactic/structural/semantic-local
categories:

- **Verification mode** is checked to be one of the known modes (the secure default,
  or the explicit insecure opt-out) — semantic-local validation, no network
  involved.
- **A custom CA bundle path**, when supplied, is checked for:
  - **existence** — the path must point to something that exists.
  - **readability** — the SDK must be able to read it.

  Both checks happen once, as part of `Configuration` resolution (see
  [Configuration Integration](#configuration-integration)) — not repeated later.
- **No certificate-content validation.** The bundle's contents are not parsed,
  decoded, or otherwise inspected at this stage — that belongs to the future
  Transport specification that actually establishes a connection.
- **No network validation and no reachability checks.** Nothing here confirms that a
  host is reachable or that a certificate is actually accepted by a real system.
- **Fail fast:** invalid TLS-related configuration (e.g. a specified CA bundle path
  that does not exist or cannot be read) is rejected immediately, as part of
  `Configuration` resolution, per [SPEC-000](design-principles.md).

## Error Behaviour

This specification describes error categories conceptually. It does **not** define
exception class names or a class hierarchy — that belongs to a future
exception-handling specification, consistent with
[SPEC-001](sdk-client.md#public-api) and
[SPEC-002](configuration.md#error-behaviour).

TLS-specific categories, in addition to the general categories
[SPEC-002](configuration.md#error-behaviour) already defines for `Configuration` as
a whole:

- **Invalid verification mode** — a value other than the known secure default or the
  explicit insecure opt-out.
- **CA bundle path missing, non-existent, or unreadable** — a custom CA bundle path
  was supplied but fails the local checks in [Validation](#validation).

In every category, resolution fails immediately and explicitly (Fail Fast), exactly
as [SPEC-002](configuration.md#error-behaviour) already describes for `Configuration`
generally.

## Testability

- TLS-related configuration must be fully testable offline — no real network or
  live certificate infrastructure required.
- Tests can construct TLS-related configuration directly, including a CA bundle path
  pointing at a local test fixture file — local filesystem checks are not a network
  dependency.
- No real certificates, CA bundles, or hosts are used in this specification or in
  any test; placeholders only.
- The insecure-mode warning (see
  [Certificate Verification](#certificate-verification)) must itself be verifiable
  by a test — for example, that enabling the insecure mode produces a warning, and
  that the warning contains no secret or target URL — without requiring a real
  insecure connection to exist.
- Validation must be deterministic: the same inputs always produce the same result,
  consistent with [SPEC-002](configuration.md#testability).

## Examples

Pseudocode only — illustrative of intended usage, not a committed API surface, not a
real implementation, and not a claim about any concrete field name, library, or file
format. Placeholder values only; no real certificates or hosts.

**Default, secure TLS (no explicit TLS configuration needed):**

```python
configuration = Configuration(
    connection=...,
    authentication=...,
    tls=...,  # defaults apply: certificate + hostname verification enabled,
    # system trust store
    logging=...,
)
```

**Custom CA bundle (e.g. for a self-signed certificate):**

```python
configuration = Configuration(
    ...,
    tls=...,  # a custom CA bundle path (str or pathlib.Path); replaces the system
    # trust store; existence/readability checked locally at Configuration creation
)
```

**Explicit insecure opt-out (exceptional cases only):**

```python
configuration = Configuration(
    ...,
    tls=...,  # explicit, deliberate opt-out of verification — never the default;
    # reserved for exceptional cases (e.g. test/lab environments); produces a clear
    # warning at client creation / transport initialization, without secrets or
    # target URLs in the warning text
)
```

## Open Questions

These are explicitly undecided. They must not be resolved silently by
implementation; each requires an explicit decision (and, where architecturally
significant, an ADR) before it can move out of this list.

- **Additional insecure-mode safeguards.** Whether the insecure mode should carry
  protections beyond the required warning (see
  [Certificate Verification](#certificate-verification)).
- **CA bundle file format(s).** Whether custom CA bundle files are limited to PEM,
  or additional formats are also supported (see [Trust Store](#trust-store)).
- **Configurable minimum TLS version.** Whether the minimum TLS version floor
  becomes configurable in a future version, rather than fixed.

## Future Extensions (non-binding)

These are possible ideas for later, explicitly non-binding, and do not represent any
architectural decision or part of SPEC-004:

- Mutual TLS (mTLS).
- Client certificates.
- Certificate pinning.
- OCSP.
- CRL.
- Configurable cipher suites.
- Configurable TLS version.
- Organization-wide TLS policies.

## Non-Goals

This specification, and by extension `TLS` itself, explicitly does not cover:

- HTTP.
- Concrete HTTP clients.
- Transport implementation.
- Cryptography implementation.
- Certificate acquisition.
- Certificate renewal.
- OCSP.
- CRL.
- Certificate pinning.
- The exception hierarchy.

Also explicitly not part of version 1 (see
[Future Extensions](#future-extensions-non-binding)):

- mTLS.
- Client certificates.

## References

- [SPEC-000 — Design Principles](design-principles.md)
- [SPEC-001 — SDK Client](sdk-client.md)
- [SPEC-002 — Configuration](configuration.md)
- [Architecture Overview](../architecture/overview.md)
- [Component Model](../architecture/components.md)
- No existing ADR (see [docs/adr/](../adr/README.md)) is specific to TLS
  architecture; none is referenced here as directly applicable.
