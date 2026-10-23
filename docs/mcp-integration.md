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
        "<path-to-sketchwright-mcp>",
        "sketchwright",
        "mcp"
      ]
    }
  }
}
```

### Google Antigravity / VS Code Configuration
Add to your project's `.agents/mcp_config.json` or client settings:

```json
{
  "mcpServers": {
    "sketchwright": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "<path-to-sketchwright-mcp>",
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

2. **`sketchwright_update_diagram`**
   - **Arguments**:
     - `specification`: (required) existing canonical JSON specification
     - `patch`: (required) update patch (`add_nodes`, `update_nodes`, `remove_nodes`, `add_edges`, `remove_edges`)
     - `generate_scene`: (optional, default `true`)
     - `output_path`: (optional) destination path
     - `overwrite`: (optional, default `false`)
   - **Returns**: `{"updated_specification": {...}, "scene": {...}, "summary": {...}}`

3. **`sketchwright_validate_diagram`**
   - **Arguments**: `specification` or `scene`
   - **Returns**: `{"is_valid": true, "errors": [], "warnings": [], "stats": {...}}`

4. **`sketchwright_layout_diagram`**
   - **Arguments**: `specification`, optional `algorithm`, `direction`
   - **Returns**: `{"node_positions": {...}, "routes": [...], "canvas": {...}}`

5. **`sketchwright_export_diagram`**
   - **Arguments**: `specification` or `scene`, `format` ("excalidraw" or "svg"), `output_path`, `overwrite`
   - **Returns**: `{"format": "...", "output_file": "...", "content_preview": "..."}`

6. **`sketchwright_get_capabilities`**
   - **Arguments**: none
   - **Returns**: dynamic capabilities manifest including shapes, algorithms, directions, formats, and limits.

## MCP Resources

- **`schema://v1.0`**: Authoritative canonical JSON schema definition for `DiagramSpec`.
- **`capabilities://manifest`**: Active runtime capability manifest and security limits.
- **`guide://usage`**: Comprehensive diagram engineering guide and best-practice patterns.

## MCP Prompts

- **`architecture_diagram`**: Standardized prompt template for requesting software architecture diagrams.
- **`flowchart_diagram`**: Prompt template for decision trees and process workflows.
- **`dependency_graph`**: Prompt template for package and module dependency graphs.

## Transport Stdio Discipline

The MCP stdio specification requires that standard output (`stdout`) be reserved strictly for JSON-RPC messages. In Sketchwright:
- All debug, info, warning, and error logs are routed exclusively to `sys.stderr`.
- Progress banners and diagnostic tables are suppressed when running in MCP mode.

