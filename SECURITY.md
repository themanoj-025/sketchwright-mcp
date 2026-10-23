# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in Sketchwright, please report it responsibly:
- **Do not open a public GitHub issue.**
- Email the maintainers directly at `code.me.025@gmail.com`.
- Include detailed steps to reproduce, affected versions, and potential impact.

We will acknowledge receipt within 48 hours and work with you to publish a coordinated advisory and fix.

## Security Architecture

1. **Strict Resource Limits**:
   - Max input payload: 1 MB (`SKETCHWRIGHT_MAX_INPUT_BYTES`)
   - Max nodes: 500 (`SKETCHWRIGHT_MAX_NODES`)
   - Max edges: 1000 (`SKETCHWRIGHT_MAX_EDGES`)
   - Max label length: 256 characters (`SKETCHWRIGHT_MAX_LABEL_LENGTH`)

2. **Filesystem Isolation**:
   - Atomic file creation via unique temporary files in the destination directory, followed by atomic replacement.
   - Normalization and validation of requested paths to protect against path traversal attacks.

3. **Execution Safety**:
   - Zero dynamic code evaluation (`eval`, `exec`).
   - Zero shell execution from diagram content.
   - MCP protocol standard output isolation to prevent sensitive data leakage.
