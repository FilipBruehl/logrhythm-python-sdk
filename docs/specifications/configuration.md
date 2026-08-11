# SPEC-002 — Configuration

| Field | Value |
| --- | --- |
| ID | SPEC-002 |
| Status | Accepted |
| Phase | A.2.3 |
| Component | Configuration |
| Depends on | [SPEC-000](design-principles.md), [SPEC-001](sdk-client.md), [SPEC-003](authentication.md), [SPEC-004](tls.md), [SPEC-005](transport.md), [SPEC-006](logging.md), [SPEC-007](exceptions.md), [SPEC-008](models.md), [SPEC-010](api-modules.md), [ADR-0007](../adr/0007-configuration-file-formats.md), [ADR-0008](../adr/0008-require-https-for-sdk-managed-endpoints.md) |
| Implementation | Not implemented |

## Status

Accepted — target architecture, not yet implemented. This specification has been
reviewed against the [Review Criteria](README.md#review-criteria) and is binding for
the Configuration Foundation implementation. Its version 1 schema, sources,
validation boundaries, and integration surface are closed.

## Purpose

`Configuration` is the immutable, validated, resolved representation of all SDK
settings. It gives `LogRhythmClient` and its shared infrastructure one source of
truth instead of allowing components to read files or ambient state independently.

Configuration resolution performs local work only. It does not contact a server,
authenticate, create a transport, initialize logging handlers, or own resources.

## Scope

This specification defines:

- the complete version 1 configuration schema;
- direct programmatic construction and loading from one configuration file;
- documented defaults and local validation;
- source-aware filesystem path resolution;
- file parsing and duplicate-key policy;
- secret-safe representation and error translation;
- the boundary with `LogRhythmClient.from_config(...)`; and
- the API-area enablement and path-override input consumed by SPEC-010.

It does not implement authentication headers, TLS contexts, HTTP transport, logging
handlers, API clients, endpoint discovery, or any network validation.

## Model Foundation

`Configuration` and every nested configuration model inherit
`InternalModel` from [SPEC-008](models.md#internal-models). Consequently they use
Pydantic v2, are frozen and keyword-only, and use the normal Pydantic validation
semantics defined by SPEC-008. Configuration does not introduce global strict mode
or a second model foundation.

Every configuration model uses the internal-model unknown-field policy
`extra="forbid"` and additionally hides raw input values from rendered Pydantic
validation errors. Unknown keys at any nesting level are validation failures. This
Pydantic setting is defense in depth only; the security boundary defined under
[Pydantic Validation Boundary](#pydantic-validation-boundary) provides the actual
guarantee that raw input-bearing validation errors are not exposed. The
model-specific boundary does not change the shared model foundation or validation
semantics. The models are fully typed and no partially valid instance is produced.

`Configuration` itself is the resolved model. There is no second public
`ResolvedConfiguration` type. Parser output and other raw mappings are inputs, not
configuration objects.

## Configuration Schema

The version 1 hierarchy is:

```text
Configuration
├── logrhythm: LogRhythmSettings
│   ├── base_url: str
│   ├── port: int
│   ├── authentication: AuthenticationSettings
│   │   └── bearer_token: SecretStr
│   ├── tls: TlsSettings
│   │   ├── verify: bool = true
│   │   └── ca_bundle: Path | None = None
│   └── timeouts: TimeoutSettings
│       ├── connect: float = 10.0
│       ├── read: float = 120.0
│       ├── write: float = 120.0
│       └── pool: float = 10.0
├── logging: LoggingSettings
│   ├── enabled: bool = false
│   ├── level: LogLevel = INFO
│   ├── format: LogFormat = Text
│   ├── file: Path | None = None
│   ├── console: bool = false
│   ├── rotation: LoggingRotationSettings
│   │   ├── max_file_size_bytes: int = 10485760
│   │   └── backup_count: int = 5
│   └── debug: LoggingDebugSettings
│       ├── include_bodies: bool = false
│       └── max_body_size_bytes: int = 16384
└── apis: ApiSettings
    ├── admin: ApiAreaSettings
    ├── drilldown: ApiAreaSettings
    ├── metrics: ApiAreaSettings
    ├── aie: ApiAreaSettings
    ├── alarms: ApiAreaSettings
    ├── cases: ApiAreaSettings
    └── search: ApiAreaSettings
```

`logrhythm` and its `base_url`, `port`, `authentication`, and `bearer_token` values
are required. The `tls`, `timeouts`, `logging`, and `apis` blocks may be omitted;
their documented resolved defaults are still present in `Configuration`.

An equivalent configuration-file shape is:

```yaml
logrhythm:
  base_url: "https://example.invalid"
  port: 8501
  authentication:
    bearer_token: "placeholder-token"
  tls:
    verify: true
    ca_bundle: null
  timeouts:
    connect: 10.0
    read: 120.0
    write: 120.0
    pool: 10.0

logging:
  enabled: false
  level: INFO
  format: Text
  file: null
  console: false
  rotation:
    max_file_size_bytes: 10485760
    backup_count: 5
  debug:
    include_bodies: false
    max_body_size_bytes: 16384

apis:
  admin:
    enabled: false
  drilldown:
    enabled: false
  metrics:
    enabled: false
  aie:
    enabled: false
  alarms:
    enabled: false
  cases:
    enabled: false
  search:
    enabled: false
```

The seven API keys are the exact public namespaces fixed by
[SPEC-010](api-modules.md#supported-apis). No other API area is accepted.

## System Endpoint

Version 1 configures one central LogRhythm system:

```text
base_url = HTTPS scheme + host
port     = one global TCP port
```

`base_url` is a required canonical origin string such as
`https://example.invalid`. It must:

- use the literal `https` scheme required by
  [ADR-0008](../adr/0008-require-https-for-sdk-managed-endpoints.md);
- contain a host;
- contain no port, user information, path, query, or fragment; and
- contain no trailing slash.

There is no implicit HTTP-to-HTTPS rewrite. `port` is separate, required, and has
no product-specific default; its resolved value is an integer in the inclusive
range 1 through 65535.

All seven API areas use this same `base_url` and `port`. Per-API hosts and ports,
multiple systems, and distributed-deployment routing are future scope and have no
version 1 abstraction.

## Authentication

Version 1 supports only the bearer-token mechanism owned by
[SPEC-003](authentication.md). `logrhythm.authentication.bearer_token` is required,
must be non-empty, and is represented by Pydantic `SecretStr`.

Configuration stores the credential but does not create an `Authorization` header
or validate it against a server. Those responsibilities remain with Transport.

## TLS

The TLS block exposes the policy owned by [SPEC-004](tls.md):

- `verify` defaults to `true` and is the single certificate/hostname-verification
  switch;
- `ca_bundle` is optional and defaults to `None`;
- when supplied, a custom CA bundle replaces the system trust source as defined by
  SPEC-004; and
- `verify=false` remains HTTPS-only and does not permit `http`.

Configuration resolves a custom CA path and performs SPEC-004's local existence and
readability checks. It does not create TLS contexts, inspect certificate contents,
perform a handshake, or expose a configurable minimum TLS version.

## Timeouts

The timeout block is optional and each value may be overridden independently. The
resolved configuration always contains all four finite, positive values.

[SPEC-005](transport.md#timeout-handling) owns timeout semantics and the defaults:

| Category | Default seconds |
| --- | ---: |
| Connect | 10.0 |
| Read | 120.0 |
| Write | 120.0 |
| Pool | 10.0 |

Each input must be numeric, finite, and greater than zero. `None`, zero, negative
values, infinity, NaN, an unlimited mode, a single combined timeout shortcut, and
an invented maximum are not supported.

## Logging Configuration

The logging block is optional. Its fields expose the configuration that
[SPEC-006](logging.md) owns; SPEC-002 does not establish competing logging
semantics or defaults.

The resolved values shown in the schema project SPEC-006's defaults: SDK-owned
logging disabled, level `INFO`, format `Text`, no file, console disabled, size-based
rotation at 10 MiB with five backups, request and response bodies excluded, and a
16 KiB per-body limit if body logging is later explicitly enabled. SPEC-006 remains
their sole semantic source of truth. `LogLevel` accepts exactly `DEBUG`, `INFO`,
`WARNING`, `ERROR`, and `CRITICAL`; `LogFormat` accepts exactly `Text` and `JSON`.

`max_file_size_bytes` and `max_body_size_bytes` must be positive integers;
`backup_count` must be a non-negative integer. Unknown logging keys, invalid field
types, unsupported level/format values, invalid numeric bounds, and a syntactically
invalid `file` value are ordinary configuration-schema failures and surface as
`ConfigurationValidationError`.

The logging-specific operational invariant remains owned by SPEC-006: when
`enabled=true`, `file` must be present and later prove usable. A missing `file` is
determinable without filesystem access and fails at Configuration construction as
`LoggingConfigurationError`, not as ordinary configuration validation. A
structurally valid path is resolved here, but its filesystem usability, writability,
and handler initialization are checked only when logging infrastructure is built;
those failures also surface as `LoggingConfigurationError`. Configuration performs
no file creation, writability check, or handler initialization.

## API Configuration

`ApiAreaSettings` has this resolved shape for every API area:

```text
enabled: bool = false
path: str | None = None
```

The input `apis` block and any individual known API entry may be omitted. Resolution
still creates all seven entries with `enabled=false` and `path=None`; omission never
creates an unknown enablement state. No API is activated implicitly.

For diagnostics required by SPEC-010, an implementation may retain internally
whether an API entry was present in the active input source. That source-presence
fact does not alter the resolved `ApiAreaSettings`, is not a public provenance API,
and is not a second enablement state.

## API Paths

The responsible API module, backed by official API documentation, owns its canonical
default path. Configuration never duplicates or invents canonical default paths; it
only carries an optional explicit override.

- With `enabled=true`, `path=None` is valid. The API module's canonical default path
  is used later. A supplied path explicitly overrides it.
- With `enabled=false`, `path` must be `None`; a supplied path is a configuration
  validation failure.

An override is a non-empty relative path without a leading or trailing slash. It:

- contains no scheme, host, port, user information, query, or fragment;
- contains no empty, `.` or `..` segment; and
- may contain nested segments separated by `/`.

No silent normalization occurs. Transport owns later URL composition and inserts
the required separator.

## Configuration Sources

Version 1 has exactly two construction sources:

1. **Programmatic:** the caller constructs `Configuration` directly from Python
   values.
2. **File:** an internal loader resolves one file into one `Configuration` for
   `LogRhythmClient.from_config(path)`.

Documented defaults fill omitted optional fields but are not a source. Version 1
has no environment-variable source, auto-discovery, default-file search, multi-file
merge, layered configuration, profile selection, dynamic reload, or remote source.
The two construction sources are never merged.

## File Loading

[ADR-0007](../adr/0007-configuration-file-formats.md) owns the supported formats.
Dispatch uses only the exact filename extension:

| Extension | Parser |
| --- | --- |
| `.yaml`, `.yml` | PyYAML safe loading |
| `.json` | Python standard-library `json` |
| `.toml` | Python standard-library `tomllib` |

There is no content detection and no additional parser dependency. Files are read
explicitly as UTF-8; no locale-dependent decoding is permitted. No special UTF-8
BOM behavior is required beyond the selected parser's normal behavior.

After parsing, the root must be a mapping/object. Empty files, a `null`/`None`
result, scalar roots, and sequence roots are invalid format input. Duplicate keys
at any mapping/object nesting level are invalid in every supported format and must
not be silently overwritten. The implementation uses parser-local detection: an
`object_pairs_hook` for JSON, a local safe-loader customization for YAML, and
`tomllib`'s native duplicate-key rejection for TOML. No general parser abstraction
is required.

## Relative Path Resolution

Filesystem paths are resolved before the final `Configuration` is returned:

- for file input, relative `tls.ca_bundle` and `logging.file` paths resolve against
  the directory containing the configuration file;
- for direct programmatic construction, relative paths resolve against the process
  current working directory at construction/validation time; and
- absolute paths remain absolute.

The resolved model stores absolute `Path` values. It does not retain a relative path
whose meaning could later change with the process working directory.

The internal file loader may carry source context while resolving paths. It does not
expose a public source or path-context object.

## Source Traceability

The implementation retains only the internal source category needed to distinguish
`programmatic` from `file` for path resolution and safe diagnostics. It exposes no
public source metadata, per-field provenance, merge history, or full raw input.

Diagnostics may identify the source category and a safe caller-supplied path when
necessary, but `repr()` does not include an unnecessary absolute configuration-file
path or any secret-bearing configuration dump.

## Public and Internal Interface

Direct construction is public through the stable facade:

```python
from logrhythm_sdk.configuration import Configuration
```

`Configuration` is not mass-re-exported from the package root and callers do not
import its implementation from `logrhythm_sdk.core`.

The file loader is internal under `logrhythm_sdk.core.configuration`. Its functional
boundary is conceptually `path -> Configuration`; its exact private helper names may
remain implementation details. Neither `Configuration.from_file(...)` nor a loader
function is added as another public SDK surface in B.1.3.

The public file-based client boundary remains:

```python
LogRhythmClient.from_config(path)
```

That factory passes the path to the internal loader, receives one validated
`Configuration`, builds the remaining shared infrastructure, and delegates to the
primary client constructor. Until the `LogRhythmClient` runtime phase, B.1.3
implements the model and internal loader but not this client factory.

## Validation

Resolution fails fast for every error determinable locally, including:

- an invalid scheme or base URL shape;
- a missing or invalid port;
- unknown or missing fields;
- missing or empty bearer token;
- invalid TLS or filesystem-path input;
- non-finite or non-positive timeout values;
- structurally or syntactically invalid logging values;
- an invalid API path or a path on a disabled API;
- an unsupported extension, decoding or parser error, duplicate key, invalid root,
  or empty/null file.

Validation performs no network request, reachability test, TLS handshake, remote
credential check, API endpoint existence check, API-version detection, file write,
or logging-handler initialization.

## Error Behaviour

All supported Configuration construction paths use only the hierarchy defined by
[SPEC-007](exceptions.md#configuration-errors):

| Failure | Public exception |
| --- | --- |
| File missing, unreadable, or other source I/O failure | `ConfigurationSourceError` |
| Unsupported extension, decoding/syntax failure, duplicate key, non-mapping root, empty/null content | `ConfigurationFormatError` |
| Input violates the general configuration schema | `ConfigurationValidationError` |
| SDK logging is enabled but `file` is absent | `LoggingConfigurationError` |
| A structurally valid logging file path is unusable, unwritable, or cannot initialize a handler | `LoggingConfigurationError` at logging initialization |

Schema violations include the HTTPS, port, unknown-field, required-token, timeout,
logging field-value, and API-path rules in this specification. The special
logging-file invariant is not reclassified as a general schema failure. The loader
does not use a catch-all translation that hides programming errors.

## Pydantic Validation Boundary

`Configuration` remains an `InternalModel`, but it is also a credential-bearing
public component. Its supported public construction boundary is therefore a more
specific rule of the kind [SPEC-008](models.md#validation) permits: a recognized
Pydantic validation failure from direct `Configuration(...)` construction is an
internal detail and is translated to a sanitized `ConfigurationValidationError`.
The native `pydantic.ValidationError` is never exposed from this supported public
boundary. The logging-file invariant instead uses `LoggingConfigurationError` as
defined under [Logging Configuration](#logging-configuration).

The internal file loader uses that same Configuration construction boundary after
parsing and path resolution. It propagates the resulting sanitized
`ConfigurationValidationError` or `LoggingConfigurationError` unchanged; it does not
create a second validation policy. Thus equivalent invalid schema input has the same
public SDK exception category whether supplied programmatically or through a file.

Pydantic validation details may be inspected only internally to produce a minimal,
safe summary. Raw input values, the unfiltered result of `ValidationError.errors()`,
and the original input-bearing Pydantic exception are discarded before the SDK
exception crosses the boundary. The exposed exception's message and structured
fields contain only sanitized information.

The normal [SPEC-007](exceptions.md#exception-chaining) preference for exception
chaining applies only when the cause and all of its reachable data are known to be
secret-free. An input-bearing Pydantic or parser exception is not chained and must
not remain reachable through either `__cause__` or `__context__`. The sanitized SDK
exception is raised outside the active handling context, or by an equivalent
mechanism that guarantees both attributes are absent or refer only to a separately
sanitized, secret-free exception. Known secret-free source errors may still be
chained. Unknown programming errors are not translated.

## Secret Safety

The bearer token is always a secret value. Configuration and its loader must never:

- expose it through `repr()`, `str()`, logs, exception messages, or diagnostics;
- retain it in structured exception fields, `__cause__`, `__context__`, Pydantic
  `errors()` data, or comparable publicly reachable error data;
- emit an unfiltered full configuration or raw parser mapping;
- serialize it unintentionally; or
- reproduce it when summarizing a parser or validation failure.

Tests use placeholder tokens and verify model representation, translated exception
messages and fields, cause/context reachability, and the absence of raw structured
Pydantic input. Secret storage uses `SecretStr`, and `hide_input_in_errors=True`
remains defense in depth; neither replaces the sanitized component boundary and no
competing secret container is introduced.

## Immutability and Lifecycle

A successfully constructed `Configuration` never mutates. To pick up changed input,
the caller constructs or loads a new instance. Configuration owns no file handle,
network connection, TLS context, logger, transport, or other resource and requires
no cleanup.

## Testability

The schema, every validation rule, all parser paths, duplicate-key handling, source
mapping, exception translation, path resolution, defaults, immutability, and secret
safety are deterministic and testable offline. Tests use temporary local files and
synthetic values only; they never use the real process environment as an implicit
configuration source and never make network calls.

## Open Questions

There are no open questions blocking or belonging to the version 1 Configuration
Foundation. Future ideas below are non-binding and require their own scoped design
work before implementation.

## Future Extensions (non-binding)

- Environment-variable or secret-manager sources.
- Named profiles or layered/multi-file configuration.
- Auto-discovery or a default configuration-file search.
- Dynamic reload.
- Multiple-system or distributed-deployment routing.
- Additional authentication mechanisms.

## Non-Goals

- Runtime client, authentication-header, transport, TLS-context, logging-handler,
  API-client, or API-resource implementation.
- Network or server-side validation.
- A public file-loader API or package-root mass export.
- Implicit configuration, silent normalization, or invented vendor values.

## References

- [SPEC-000 — Design Principles](design-principles.md)
- [SPEC-001 — SDK Client](sdk-client.md)
- [SPEC-003 — Authentication](authentication.md)
- [SPEC-004 — TLS](tls.md)
- [SPEC-005 — Transport](transport.md)
- [SPEC-006 — Logging](logging.md)
- [SPEC-007 — Exception Handling](exceptions.md)
- [SPEC-008 — Models](models.md)
- [SPEC-010 — API Modules](api-modules.md)
- [Architecture Overview](../architecture/overview.md)
- [Component Model](../architecture/components.md)
- [ADR-0007 — Support YAML, JSON, and TOML configuration files](../adr/0007-configuration-file-formats.md)
- [ADR-0008 — Require HTTPS for SDK-managed LogRhythm endpoints](../adr/0008-require-https-for-sdk-managed-endpoints.md)
