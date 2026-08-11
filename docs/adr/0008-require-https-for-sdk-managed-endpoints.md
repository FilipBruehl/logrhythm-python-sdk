# 0008. Require HTTPS for SDK-managed LogRhythm endpoints

## Status

Accepted

## Context

The SDK's configuration and transport architecture needs a binding policy for the
scheme of LogRhythm endpoints. [SPEC-005](../specifications/transport.md) already
places URL resolution in the central transport and defines a transport profile as
including a scheme, host, port, and TLS configuration, but it does not decide which
schemes version 1 accepts. [SPEC-002](../specifications/configuration.md) likewise
requires local configuration validation without yet defining the concrete endpoint
schema.

Version 1 uses bearer-token authentication
([SPEC-003](../specifications/authentication.md)). Allowing a configured plain-HTTP
origin would permit credentials, requests, and responses to cross the network
without transport encryption. A warning would describe that risk but would not
prevent it. The initial configuration contract therefore needs an explicit,
fail-secure scheme boundary before Configuration or Transport is implemented.

[SPEC-004](../specifications/tls.md) separately permits an explicit insecure mode
that disables certificate and hostname verification. That mode changes how an
HTTPS peer is authenticated; it does not decide whether transport encryption is
used. The endpoint-scheme policy must keep those two concerns distinct.

No Configuration or Transport runtime has shipped, so this decision establishes
the initial version 1 contract rather than changing an existing public behavior.

## Decision

All SDK-managed LogRhythm endpoints use HTTPS in version 1. The only supported
scheme for a LogRhythm origin accepted by SDK Configuration is `https`. A plain
HTTP origin, or any other endpoint scheme, is invalid and fails local configuration
validation before Transport is created or any network request occurs.

Conceptually:

```text
https://sdk.example.invalid  -> valid scheme
http://sdk.example.invalid   -> invalid scheme
```

Configuration owns this validation boundary. Transport receives an already
validated HTTPS origin and does not define a competing scheme policy. The SDK does
not silently rewrite `http` to `https`.

Transport encryption and peer verification remain separate controls:

- HTTPS with certificate and hostname verification enabled is the default.
- HTTPS with the explicit verification opt-out from SPEC-004 remains permitted.
- Disabling certificate or hostname verification does not disable transport
  encryption and does not permit plain HTTP.

Consequently, the SDK architecture does not intentionally transmit bearer
credentials over unencrypted plain HTTP. This decision does not otherwise change
how credentials are represented, stored, or applied.

This ADR decides only the allowed endpoint scheme. SPEC-002 remains responsible for
the concrete Configuration field names and origin schema, and SPEC-005 remains
responsible for URL composition and request execution.

## Alternatives

### Support HTTP and HTTPS

Supporting both schemes would maximize compatibility, including with historical or
isolated deployments. It would also permit unencrypted bearer credentials, API
requests, and API responses, enlarge the security and test matrix, and make an
unsafe deployment easier to configure accidentally. Rejected for version 1.

### Support HTTP with a warning

A warning would make the unsafe state visible but would not prevent credentials or
API data from being transmitted without encryption. It would therefore not provide
the fail-secure boundary required of the SDK's initial configuration contract.
Rejected.

### Require HTTPS

Requiring HTTPS establishes encrypted transport as the single version 1 baseline,
keeps configuration behavior deterministic, and reduces both misconfiguration
surface and the number of transport combinations that must be supported. Accepted.

## Consequences

- Every SDK-managed LogRhythm origin is validated as HTTPS before Transport uses
  it.
- Plain HTTP cannot be enabled through a warning, a verification setting, or silent
  scheme normalization.
- Bearer credentials are not intentionally transmitted by the SDK over
  unencrypted plain HTTP.
- API requests and responses have transport encryption as a mandatory baseline.
- The supported configuration and transport test matrix is smaller and less
  ambiguous.
- HTTP-only deployments cannot be used with version 1 of the SDK.
- Local test systems also need HTTPS.
- Certificate problems are addressed through the TLS configuration already defined
  by SPEC-004, such as a custom CA bundle or its explicit verification opt-out, not
  by switching to HTTP.
- This is not a breaking change because no Configuration or Transport runtime with
  HTTP support has shipped.
- Supporting plain HTTP or another endpoint scheme in the future requires an
  explicit architecture review and corresponding normative change before
  implementation. No speculative abstraction is introduced for that possibility.

This ADR does not decide ports, API-specific paths, timeout values, CA-bundle
formats, cipher suites, configurable TLS minimum versions, proxies, mTLS, HTTP/2,
HTTP/3, certificate pinning, authentication providers, per-API hosts or ports, or
distributed deployments.

## References

- [ADR Policy](README.md#when-an-adr-is-required)
- [ADR-0006 — Use HTTPX as HTTP transport library](0006-httpx-transport.md)
- [SPEC-000 — Design Principles](../specifications/design-principles.md)
- [SPEC-002 — Configuration](../specifications/configuration.md)
- [SPEC-003 — Authentication](../specifications/authentication.md)
- [SPEC-004 — TLS](../specifications/tls.md)
- [SPEC-005 — Transport](../specifications/transport.md)
- [SPEC-007 — Exception Handling](../specifications/exceptions.md)
