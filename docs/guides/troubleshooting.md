# Troubleshooting Guide

Common issues encountered when installing, running, or integrating Sketchwright, along with proven remedies.

---

### 1. `ValidationError: Input size exceeds maximum limit`
- **Cause**: Input JSON or text DSL exceeds the configured input size limit (default 1 MB).
- **Resolution**: Optimize or split your diagram specification, or increase the limit by setting:
  ```powershell
  $env:SKETCHWRIGHT_MAX_INPUT_BYTES="5242880"  # 5 MB
  ```

---

### 2. `FileSystemError: Destination file already exists`
- **Cause**: The CLI or API was instructed to write to a path that already exists, and overwrite protection was active.
- **Resolution**:
  - In the CLI, supply the `--overwrite` flag:
    ```bash
    uv run sketchwright generate spec.json -o diagram.excalidraw --overwrite
    ```
  - In the Python API, pass `overwrite=True`:
    ```python
    generate_diagram(spec, output_path="diagram.excalidraw", overwrite=True)
    ```

---

### 3. MCP Server Fails to Connect in Host
- **Symptoms**: Host reports `Failed to initialize server` or JSON-RPC handshake timeout.
- **Diagnostic Steps**:
  1. Verify the launch command from terminal:
     ```powershell
     uv run --directory F:/GITHUB/sketchwright-mcp sketchwright mcp
     ```
  2. Ensure the working directory exists and is accessible.
  3. Verify that your host configuration uses forward slashes in paths:
     ```json
     "args": ["run", "--directory", "F:/GITHUB/sketchwright-mcp", "sketchwright", "mcp"]
     ```
  4. Ensure stdout is clean. In Sketchwright, all logs are routed to `stderr` by design.

---

### 4. `ValidationError: Duplicate node IDs detected`
- **Cause**: Two nodes in the `nodes` array share the same `id`.
- **Resolution**: Ensure every node has a unique `id` attribute. Labels can be identical, but identifiers must be distinct.

---

### 5. `Arrow has dangling startBinding or endBinding`
- **Cause**: An edge references a node `source` or `target` that was not defined in the `nodes` array.
- **Resolution**: Add the missing node to `nodes`, or correct the endpoint identifier on the edge.
