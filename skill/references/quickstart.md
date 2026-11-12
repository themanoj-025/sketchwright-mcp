# Sketchwright Quickstart Guide for Buyers

Thank you for purchasing **Sketchwright: Excalidraw Diagram Engine**!

This skill equips your AI coding agent (Claude Code, Cursor, GitHub Copilot, Codex, etc.) with the ability to generate clean, deterministic, editable Excalidraw diagram files (`.excalidraw`) and standalone SVGs.

---

## 1. Quick Setup (1 Minute)

Ensure you have Python 3.12+ and [uv](https://docs.astral.sh/uv/) installed:
```bash
# Verify uv is installed
uv --version
```

### For Claude Desktop / Cursor / Antigravity / Claude Code
Add this to your MCP configuration file:
- **Claude Desktop:** `%APPDATA%\Claude\claude_desktop_config.json` (Windows) or `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)
- **Cursor:** `Settings -> Features -> MCP -> Add New MCP Server`
- **Claude Code:** Add via `claude mcp add sketchwright uvx --from git+https://github.com/manoj-025/sketchwright-mcp.git sketchwright mcp`

```json
{
  "mcpServers": {
    "sketchwright": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/manoj-025/sketchwright-mcp.git",
        "sketchwright",
        "mcp"
      ]
    }
  }
}
```

---

## 2. How to Use with Your AI Agent

Simply ask your AI assistant in plain English:

- *"Create an Excalidraw architecture diagram for my SaaS application with a React frontend, Next.js API, Redis cache, and PostgreSQL database. Save it as architecture.excalidraw."*
- *"Generate an SVG flowchart for user registration and email verification with retry logic."*
- *"Update architecture.excalidraw to add a Stripe webhook endpoint and worker queue."*

The agent will automatically use the `sketchwright_create_diagram` tool and generate the file directly in your project folder!

---

## 3. Viewing & Editing Your Diagrams
- Drag and drop `.excalidraw` files into **[excalidraw.com](https://excalidraw.com)**.
- Or install the **Excalidraw extension** in VS Code or Obsidian.
- All boxes, arrows, and texts are fully bound and editable.

