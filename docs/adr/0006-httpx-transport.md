# 0006. Use HTTPX as HTTP transport library

## Status

Accepted

## Context

[SPEC-005 — Transport](../specifications/transport.md) defines the SDK's single
HTTP boundary: a `Transport`/`HttpTransport` component that fully encapsulates URL
resolution, headers, authentication, TLS, timeouts, and response handling behind a
narrow `TransportProtocol` contract (see
[SPEC-005, Transport Model](../specifications/transport.md#transport-model)). The
SDK is synchronous in v1 (see
[Architecture Overview](../architecture/overview.md#synchronous-first)) and needs
long-lived, pooled HTTP clients per transport profile (see
[SPEC-005, HTTP Client Management](../specifications/transport.md#http-client-management)),
not a one-off request tool. An HTTP library needs to be chosen once, centrally, so
that no API module or resource ever depends on a specific HTTP library directly
(see
[SPEC-000, Stable abstractions](../specifications/design-principles.md#architecture-principles)).

## Alternatives considered

- **`requests`** — the long-standing default, but synchronous-only with no
  first-party async story, and largely in maintenance mode; would not give the
  project a natural path to a possible future asynchronous variant (see
  [SPEC-005, Future Extensions](../specifications/transport.md#future-extensions))
  without adopting a second library later.
- **`urllib3` directly** — lower-level than needed; would require hand-building the
  request/response abstraction, connection-pooling policy, and timeout handling
  that a higher-level client already provides, for no benefit specific to this SDK.
- **`aiohttp`** — async-first; would force asynchronous code even though
  [SPEC-005](../specifications/transport.md#non-goals) and the Architecture
  Overview commit to a synchronous v1, and would need a separate sync wrapper.
- **Standard library `http.client`/`urllib.request`** — no connection-pooling
  ergonomics, no HTTP/2, and minimal support for headers/timeouts/TLS
  configuration; would need substantial wrapping to meet
  [SPEC-005](../specifications/transport.md)'s requirements.

## Decision

The SDK uses **httpx** as its underlying HTTP library for v1, as already decided in
[SPEC-005 — Transport](../specifications/transport.md#transport-model). httpx
supports both a synchronous and (should it be needed later) asynchronous client
under one API, and has first-party connection pooling. httpx is fully
encapsulated: **no API module or resource ever imports httpx directly**, and **no
httpx type is ever exposed through the SDK's public API** — every API module
depends exclusively on the SDK's own `TransportProtocol` contract (see
[SPEC-005, Transport Model](../specifications/transport.md#transport-model)), never
on httpx's concrete client or response types. `Transport` owns long-lived, pooled
httpx client instances per transport profile (see
[SPEC-005, HTTP Client Management](../specifications/transport.md#http-client-management))
rather than constructing one per request. **No optional httpx extras** (e.g.
`httpx[http2]`, `httpx[brotli]`, `httpx[socks]`) are adopted as part of this
decision — only httpx's base install.

## Consequences

- httpx becomes a mandatory runtime dependency of the SDK — see
  [pyproject.toml](../../pyproject.toml).
- `Transport`/`HttpTransport` is the SDK's sole point of contact with httpx; every
  other component depends only on `TransportProtocol`, per
  [SPEC-005](../specifications/transport.md#transport-model) — this keeps httpx
  replaceable later without touching API modules.
- A future asynchronous SDK variant (see
  [SPEC-005, Future Extensions](../specifications/transport.md#future-extensions))
  can reuse httpx's async client behind the same abstraction, rather than
  requiring a second HTTP library.
- Adopting an optional httpx extra, or replacing httpx with a different HTTP
  library, would reverse or extend this decision and requires its own ADR, per
  [docs/adr/README.md](README.md#when-an-adr-is-required).
