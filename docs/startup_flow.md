# Process Startup Flow

## MCP Stdio Server Startup Flow
1. Host launches `uv run sketchwright mcp`
2. `src/sketchwright/cli.py` invokes `src/sketchwright/mcp/server.py:run_server()`
3. FastMCP initializes stdio transport pipes
4. Tool handlers registered:
   - `sketchwright_generate`
   - `sketchwright_layout`
   - `sketchwright_validate`
   - `sketchwright_update`
   - `sketchwright_export`
   - `sketchwright_capabilities`
5. Server listens on `stdin` / `stdout` using JSON-RPC 2.0 frames
