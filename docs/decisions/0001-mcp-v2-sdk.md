# ADR 0001: Adoption of Official MCP 2.x Python SDK

## Context
The Model Context Protocol Python SDK evolved from version 1.x (which used `FastMCP`) to version 2.x (`mcp>=2.0.0`, currently `2.3.0`), where `FastMCP` was superseded by `MCPServer` in `mcp.server.mcpserver`.

## Decision
We adopt the current official `mcp.server.mcpserver.MCPServer` API from `mcp 2.3.0`:
- Tools are declared using `@server.tool()`.
- Resources are registered using `@server.resource()`.
- Prompts are registered using `@server.prompt()`.
- Protocol transport is invoked via `server.run(transport="stdio")`.

## Consequences
- Full compatibility with the modern MCP specification.
- Native JSON Schema generation from typed Python functions.
- Avoids legacy deprecated v1 imports.
