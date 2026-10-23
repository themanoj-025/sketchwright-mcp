# Sketchwright 📐

**Deterministic Excalidraw MCP Diagram Agent & Layout Engine**

[![CI](https://github.com/manoj-025/sketchwright-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/manoj-025/sketchwright-mcp/actions)
[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![MCP Specification](https://img.shields.io/badge/MCP-2.3.0-green.svg)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 1. Overview

**Sketchwright** is a developer-oriented Model Context Protocol (MCP) diagram agent and standalone Python engine. It translates structured diagram specifications and lightweight textual DSL into deterministic, visually balanced, and fully editable **Excalidraw-compatible scenes (`.excalidraw`)** as well as standalone **SVG**.

A language model in an MCP-compatible host decides *what* the diagram should represent; Sketchwright's deterministic engine decides *how* that specification is validated, positioned, routed, and serialized.

### Core Product Principle
> **Structured intent in; validated, editable diagram scene out.**

Core capabilities require **no paid model APIs, cloud accounts, API keys, or external LLM service**.

---

## 2. Core Features

- **Model Context Protocol (MCP 2.x) Integration**: Exposes 5 dedicated tools (`create_diagram`, `validate_diagram`, `layout_diagram`, `export_diagram`, `get_capabilities`), resources, and prompts over standard input/output transport.
- **Strict Stdio Discipline**: Guarantees that MCP JSON-RPC protocol framing is never polluted by application logs; all diagnostics are routed strictly to `sys.stderr`.
- **Deterministic Layered Layout (Sugiyama Engine)**:
  - Cycle detection and feedback edge set condensation to guarantee termination on cyclic graphs.
  - Longest-path rank assignment and barycentric crossing reduction.
  - Multi-directional flow: Left-to-Right (`LR`), Right-to-Left (`RL`), Top-to-Bottom (`TB`), and Bottom-to-Top (`BT`).
  - Graceful handling of disconnected clusters, self-loops, and parallel edges.
- **True Excalidraw v2 Schema & Reciprocal Bindings**:
  - Validates and generates native `startBinding`, `endBinding`, container `boundElements`, and centered bound text containers.
  - Fully editable in [Excalidraw.com](https://excalidraw.com) or the Excalidraw VS Code / Obsidian extensions.
- **Standalone CLI & Public Python API**: Complete standalone functionality without requiring an active MCP host.
- **Defensive Resource Limits**: Enforces input byte size, node counts, edge counts, and atomic filesystem writes to protect against path traversal and file corruption.
- **Clean SVG Export**: Standalone valid SVG renderer with correct shapes, arrow markers, and text escaping.

---

## 3. Supported Diagram Types

- **Software & Cloud Architecture**: Multi-tier web apps, client/server models, API gateways, database clusters.
- **Microservice & Data-Flow Diagrams**: Service meshes, message queues, cache layers, storage topologies.
- **Decision Trees & Process Flowcharts**: Branching logic, validation flows, decision nodes.
- **State-Transition Diagrams & Cyclic Networks**: Finite state machines, feedback loops, retry circuits.
- **CI/CD Pipelines & Roadmaps**: Build, test, security audit, and deployment stages.

---

## 4. Requirements

- **Python**: 3.12 or newer.
- **Package Manager**: [uv](https://docs.astral.sh/uv/) (recommended) or standard `pip`.
- **Operating System**: Windows (first-class support), Linux, macOS.

---

## 5. Installation

### Using uv (Recommended)

```powershell
# Clone the repository
git clone https://github.com/manoj-025/sketchwright-mcp.git
Set-Location sketchwright-mcp

# Install dependencies and sync virtual environment
uv sync --all-groups
```

### In POSIX Shells (Linux / macOS)

```bash
git clone https://github.com/manoj-025/sketchwright-mcp.git
cd sketchwright-mcp
uv sync --all-groups
```

---

## 6. Command-Line Interface (CLI)

Sketchwright includes an entry point `sketchwright` and supports module execution via `python -m sketchwright`.

### Exit Code Policy
- `0`: Success
- `2`: Validation error, syntax error, or invalid user input
- `1`: Filesystem or unexpected internal runtime error

### Commands

```powershell
# Display help and version
uv run sketchwright --help
uv run sketchwright --version

# View system capabilities and active limits
uv run sketchwright capabilities

# Validate a diagram specification or an Excalidraw scene file
uv run sketchwright validate examples/architecture.json
uv run sketchwright validate my_diagram.excalidraw

# Generate an Excalidraw diagram
uv run sketchwright generate examples/architecture.json -o web_arch.excalidraw --overwrite

# Generate an SVG diagram
uv run sketchwright generate examples/flowchart.json -o flowchart.svg --format svg --overwrite

# Compute raw geometry and routes
uv run sketchwright layout examples/architecture.json --direction LR

# Launch the MCP server over stdio
uv run sketchwright mcp
```

---

## 7. Public Python API

Sketchwright can be embedded as a standard Python library:

```python
from sketchwright import generate_diagram, validate_diagram, export_diagram

spec = {
    "schema_version": "1.0",
    "title": "Cloud Microservice Architecture",
    "layout": {"algorithm": "layered", "direction": "LR"},
    "nodes": [
        {"id": "gateway", "label": "API Gateway", "shape": "rectangle"},
        {"id": "auth", "label": "Auth Service", "shape": "rounded_rectangle"},
        {"id": "db", "label": "User Store", "shape": "cylinder"},
    ],
    "edges": [
        {"id": "e1", "source": "gateway", "target": "auth", "label": "JWT Verify"},
        {"id": "e2", "source": "auth", "target": "db", "label": "SQL Query"},
    ],
}

# 1. Generate full result
result = generate_diagram(spec, output_path="architecture.excalidraw", overwrite=True)

print(f"Valid Scene: {result.validation.is_valid}")
print(f"Canvas Size: {result.laid_out.canvas_rect.width} x {result.laid_out.canvas_rect.height}")
print(f"Total Elements: {len(result.scene['elements'])}")
```

---

## 8. MCP Host Integration

To register Sketchwright in an MCP client (such as Claude Desktop, VS Code, or Google Antigravity), add the following server configuration to your `mcpServers` settings:

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

### Implemented MCP Tools

| Tool Name | Description |
| :--- | :--- |
| `sketchwright_create_diagram` | Generates a complete Excalidraw scene JSON from a structured specification or text DSL. |
| `sketchwright_update_diagram` | Incrementally updates an existing diagram specification (add/remove/rename nodes, add/remove edges) and regenerates scene. |
| `sketchwright_validate_diagram` | Validates a diagram specification or Excalidraw scene for schema conformance, bindings, and geometry. |
| `sketchwright_layout_diagram` | Computes deterministic node coordinates, canvas bounds, and edge routes without serialization. |
| `sketchwright_export_diagram` | Exports a diagram specification or scene to `.excalidraw` or `.svg`. |
| `sketchwright_get_capabilities` | Returns machine-readable report of supported shapes, algorithms, directions, and limits. |

### MCP Resources & Prompts
- **Resources**:
  - `schema://v1.0`: Canonical JSON Schema for `DiagramSpec`.
  - `capabilities://manifest`: Runtime capability and limits manifest.
  - `guide://usage`: Comprehensive prompt engineering guide and diagram patterns.
- **Prompts**:
  - `architecture_diagram`: Prompt guide for structured software architecture requests.
  - `flowchart_diagram`: Prompt guide for workflow/decision flowcharts.
  - `dependency_graph`: Prompt guide for software/package dependency graphs.

---

## 9. Canonical Diagram Input Format

```json
{
  "schema_version": "1.0",
  "title": "Example Web Architecture",
  "layout": {
    "algorithm": "layered",
    "direction": "LR",
    "node_spacing": 80,
    "rank_spacing": 120,
    "padding": 40
  },
  "style": {
    "theme": "light",
    "font_size": 18,
    "stroke_width": 2
  },
  "nodes": [
    { "id": "browser", "label": "Web Browser", "shape": "rectangle" },
    { "id": "api", "label": "API Server", "shape": "rounded_rectangle" },
    { "id": "database", "label": "Database", "shape": "cylinder" }
  ],
  "edges": [
    { "id": "e1", "source": "browser", "target": "api", "label": "HTTPS", "kind": "directed" },
    { "id": "e2", "source": "api", "target": "database", "label": "SQL", "kind": "directed" }
  ],
  "options": {
    "deterministic": true
  }
}
```

### Supported Shapes
- `rectangle`: Standard box
- `rounded_rectangle`: Rounded container
- `ellipse`: Terminal / start / end state
- `diamond`: Decision condition
- `cylinder`: Storage / Database (modeled with adaptive rounded container)
- `text`: Standalone text note

---

## 10. Testing & Verification

Sketchwright includes a comprehensive test suite across unit, property, contract, and e2e levels:

```powershell
# Run the entire test suite
uv run pytest -v

# Check formatting and linting
uv run ruff check .
uv run ruff format --check .

# Run static type checking
uv run mypy src

# Build package distributions
uv build
```

---

## 11. Known Limitations

1. **Approximate Font Metrics**: To avoid heavy cross-platform font rendering dependencies (like HarfBuzz/FreeType), Sketchwright uses deterministic font dimension heuristics. Browser rendering might have minor variations depending on local font fallbacks.
2. **Simplified Edge Routing**: Orthogonal stepped routing avoids node interiors and handles backward loops; complex multi-hop obstacle avoidance routes around rank boundaries rather than sub-pixel collision routing.
3. **No Automatic Host Registration**: MCP client registration requires adding the configuration snippet to your host configuration file.

---

## 12. Security Considerations

- **Strict Resource Limits**: Max input size 1MB, max 500 nodes, max 1000 edges, max label length 256.
- **Filesystem Isolation**: Writes are performed atomically using temporary files and safe atomic rename. Traversal attempts and unauthorized paths are rejected.
- **Zero Dynamic Code Execution**: No `eval`, `exec`, or dynamic imports are ever used.

---

## 13. License

Distributed under the **MIT License**. See [LICENSE](LICENSE) for details.
