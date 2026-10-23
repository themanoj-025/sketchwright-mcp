# Model Context Protocol (MCP) Integration

Sketchwright integrates with AI hosts through the official Model Context Protocol (MCP 2.3.0) Python SDK using standard input/output (`stdio`) transport.

## Server Launch Command

```bash
uv run --directory <path-to-sketchwright-mcp> sketchwright mcp
```

## MCP Client Configuration

### Claude Desktop Configuration
Add the server definition to `%APPDATA%\Claude\claude_desktop_config.json` (Windows) or `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "sketchwright": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "F:/GITHUB/sketchwright-mcp",
        "sketchwright",
        "mcp"
      ]
    }
  }
}
```

### Google Antigravity / VS Code Configuration
Add to your project's `.agents/mcp_config.json` or user settings:

```json
{
  "mcpServers": {
    "sketchwright": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "F:/GITHUB/sketchwright-mcp",
        "sketchwright",
        "mcp"
      ]
    }
  }
}
```

## Registered Tools

1. **`sketchwright_create_diagram`**
   - **Arguments**:
     - `specification`: (optional) canonical JSON specification object
     - `text_dsl`: (optional) lightweight text diagram string
     - `layout_overrides`: (optional) `{"algorithm": "layered", "direction": "LR"}`
     - `output_path`: (optional) path to save `.excalidraw` or `.svg`
     - `overwrite`: (optional, default `false`)
   - **Returns**: `{"scene": {...}, "summary": {...}, "validation": {...}}`

2. **`sketchwright_validate_diagram`**
   - **Arguments**: `specification` or `scene`
   - **Returns**: `{"is_valid": true, "errors": [], "warnings": [], "stats": {...}}`

3. **`sketchwright_layout_diagram`**
   - **Arguments**: `specification`, optional `algorithm`, `direction`
   - **Returns**: `{"node_positions": {...}, "routes": [...], "canvas": {...}}`

4. **`sketchwright_export_diagram`**
   - **Arguments**: `specification` or `scene`, `format` ("excalidraw" or "svg"), `output_path`, `overwrite`
   - **Returns**: `{"format": "...", "output_file": "...", "content_preview": "..."}`

5. **`sketchwright_get_capabilities`**
   - **Arguments**: none
   - **Returns**: dynamic capabilities manifest including shapes, algorithms, directions, formats, and limits.

## Transport Stdio Discipline

The MCP stdio specification requires that standard output (`stdout`) be reserved strictly for JSON-RPC messages. In Sketchwright:
- All debug, info, warning, and error logs are routed exclusively to `sys.stderr`.
- Progress banners and diagnostic tables are suppressed when running in MCP mode.
