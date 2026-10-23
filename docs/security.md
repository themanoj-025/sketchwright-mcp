# Security & Defensive Boundaries

Sketchwright operates as a local diagram generation engine and MCP server. It treats all external diagram specifications and MCP tool inputs as untrusted data.

## Defensive Boundaries

### 1. Resource Limits
To defend against denial-of-service via memory exhaustion or CPU hangs:
- **Max Input Payload**: 1 MB (`SKETCHWRIGHT_MAX_INPUT_BYTES`). Strings exceeding this threshold are rejected immediately before JSON decoding.
- **Max Node Count**: 500 (`SKETCHWRIGHT_MAX_NODES`).
- **Max Edge Count**: 1000 (`SKETCHWRIGHT_MAX_EDGES`).
- **Max Label Length**: 256 characters (`SKETCHWRIGHT_MAX_LABEL_LENGTH`).
- **Numeric Verification**: All coordinates and dimensions must be finite numbers; `NaN`, `+inf`, and `-inf` are rejected.

### 2. Filesystem Protection
When writing diagram files (`.excalidraw` or `.svg`):
- **Path Resolution & Normalization**: User-supplied paths are resolved to absolute paths. Traversal patterns (`../`) are validated to ensure writes occur only within intended directories.
- **Atomic File Writing**: Output is written to a hidden temporary file with a random UUID suffix in the destination directory, flushed to disk, synced via `os.fsync`, and atomically replaced via `os.replace`.
- **Overwrite Protection**: Destination files are never overwritten silently; explicit permission (`--overwrite` or `overwrite=True`) is mandatory.

### 3. Execution Safety
- **No Dynamic Evaluation**: Sketchwright contains zero calls to `eval()`, `exec()`, or `__import__()`.
- **No Subprocess Invocations from Diagram Content**: Diagram metadata cannot trigger shell commands or external scripts.
- **No Unsolicited Network Calls**: The core library operates 100% offline and makes zero telemetry or update requests.

### 4. Transport Isolation
- MCP JSON-RPC frames over `stdio` strictly utilize `sys.stdout`.
- Internal logging is redirected to `sys.stderr` to prevent protocol framing corruption.
- Sensitive environment variables and secrets are never reflected in error payloads.
