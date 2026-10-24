# Sketchwright

> Deterministic Excalidraw diagram agent, layout engine, and Model Context Protocol (MCP) server.

**Status:** Beta (v0.1.0). Fully functional MCP server, standalone Python engine, and CLI; production-ready for automated diagram generation.

[![CI](https://github.com/manoj-025/sketchwright-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/manoj-025/sketchwright-mcp/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![MCP Specification](https://img.shields.io/badge/MCP-2.3.0-green.svg)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.0-orange.svg)](./CHANGELOG.md)

<!-- TODO[L2-01]: capture a terminal recording or Excalidraw canvas screenshot (~1200px wide, showing architecture diagram export); draft alt text: "Terminal executing sketchwright generate and Excalidraw UI rendering web architecture diagram" (owner: Maintainer) -->
<!-- TODO[L2-02]: activate PyPI badge in header row once initial v0.1.0 release is published to pypi.org (owner: Maintainer) -->

---

## Quick Facts

| Dimension | Specification | Evidence / Details |
| :--- | :--- | :--- |
| **Package Name** | `sketchwright` | Defined in [`pyproject.toml`](./pyproject.toml) |
| **Runtime Requirement** | Python `>=3.12` | Tested on Python 3.12 (`ubuntu-latest`, `windows-latest`) |
| **Protocol Support** | Model Context Protocol (MCP) 2.3.0 | 6 tools, 3 resources, 3 prompts over `stdio` |
| **Output Formats** | `.excalidraw` (v2 JSON schema), `.svg` (standalone) | Verified reciprocal arrow bindings & multiline text containers |
| **Layout Algorithms** | Layered (Sugiyama), Grid, Tree | Deterministic cycle breaking, 4 directions (`LR`, `RL`, `TB`, `BT`) |
| **External Dependencies** | Zero external LLM or cloud services required | Pure local layout and scene serialization |
| **Primary Entry Points** | `sketchwright` CLI, `sketchwright` Python module | Module execution via `python -m sketchwright` |
| **License** | MIT License | Verified in [`LICENSE`](./LICENSE) |

---

## Overview

**Sketchwright** is a developer-oriented Model Context Protocol (MCP) diagram agent and standalone Python engine. It translates structured diagram specifications and lightweight textual DSL into deterministic, visually balanced, and fully editable **Excalidraw-compatible scenes (`.excalidraw`)** as well as standalone **SVG**.

A language model in an MCP-compatible host (such as Claude Desktop, VS Code, or Antigravity) decides *what* the diagram should represent; Sketchwright's deterministic engine decides *how* that specification is validated, positioned, routed, and serialized.

### Core Product Principle
> **Structured intent in; validated, editable diagram scene out.**

Core layout, validation, and generation capabilities require **no paid model APIs, cloud accounts, API keys, or external LLM service**.

---

## Quick Start

Generate a complete, editable Excalidraw diagram scene in fewer than five steps:

### In POSIX Shells (Linux / macOS)

```bash
# 1. Clone the repository
git clone https://github.com/manoj-025/sketchwright-mcp.git
cd sketchwright-mcp

# 2. Install dependencies with uv
uv sync --all-groups

# 3. Generate an Excalidraw diagram from the sample architecture
uv run sketchwright generate examples/architecture.json -o architecture.excalidraw --overwrite
```

### In PowerShell (Windows)

```powershell
# 1. Clone the repository
git clone https://github.com/manoj-025/sketchwright-mcp.git
Set-Location sketchwright-mcp

# 2. Install dependencies with uv
uv sync --all-groups

# 3. Generate an Excalidraw diagram from the sample architecture
uv run sketchwright generate examples/architecture.json -o architecture.excalidraw --overwrite
```

Expected result:
```text
Generated diagram written to: architecture.excalidraw
```

You can drag and drop `architecture.excalidraw` directly into [Excalidraw.com](https://excalidraw.com) or open it inside the Excalidraw VS Code extension.

---

## Features

- **Model Context Protocol (MCP 2.x) Integration**: Exposes 6 dedicated tools (`sketchwright_create_diagram`, `sketchwright_update_diagram`, `sketchwright_validate_diagram`, `sketchwright_layout_diagram`, `sketchwright_export_diagram`, `sketchwright_get_capabilities`), 3 resources, and 3 prompt templates over standard input/output (`stdio`).
- **Strict Stdio Discipline**: Guarantees that MCP JSON-RPC protocol framing is never polluted by application logs; all diagnostics are routed strictly to `sys.stderr`.
- **Deterministic Layered Layout (Sugiyama Engine)**:
  - Cycle detection and feedback edge set condensation to guarantee termination on cyclic graphs.
  - Longest-path rank assignment and barycentric crossing reduction.
  - Multi-directional flow: Left-to-Right (`LR`), Right-to-Left (`RL`), Top-to-Bottom (`TB`), and Bottom-to-Top (`BT`).
  - Graceful handling of disconnected clusters, self-loops, and parallel edges.
- **True Excalidraw v2 Schema & Reciprocal Bindings**:
  - Validates and generates native `startBinding`, `endBinding`, container `boundElements`, and centered bound text containers.
  - Fully editable in [Excalidraw.com](https://excalidraw.com) or the Excalidraw VS Code / Obsidian extensions.
- **Visual Grouping & Boundaries**: Declared groups serialize with member container tracking and dashed boundary rectangles.
- **Incremental Diagram Mutation**: Iteratively patch diagrams (add/remove nodes, prune connected edges, update labels) via stable ID matching with ambiguous-match fallback protection.
- **Standalone CLI & Public Python API**: Complete functionality accessible as a CLI utility or embedded library without requiring an active MCP host.
- **Defensive Resource Limits**: Enforces input payload limits (1 MB), node counts (500), edge counts (1000), label lengths (256 chars), and path traversal boundary checks.
- **Clean SVG Export**: Standalone valid SVG renderer with `<tspan>` multiline text wrapping, arrow markers, and XML escaping.

---

## Supported Diagram Types

- **Software & Cloud Architecture**: Multi-tier web applications, client/server models, API gateways, database clusters.
- **Microservices & Data-Flow Topologies**: Service meshes, message brokers, caching tiers, storage clusters.
- **Decision Trees & Process Flowcharts**: Branching logic, validation flows, decision nodes.
- **State-Transition Diagrams & Cyclic Networks**: Finite state machines, feedback loops, retry circuits.
- **CI/CD Pipelines & Roadmaps**: Build, test, security audit, and deployment stages.

### Supported Shapes

| Shape Identifier | Visual Representation | Common Use Case |
| :--- | :--- | :--- |
| `rectangle` | Standard sharp box | Services, modules, UI components, microservices |
| `rounded_rectangle` | Rounded container | Queues, consumers, workers, terminal steps |
| `ellipse` | Elliptical container | Start/stop states, events, terminal nodes |
| `diamond` | Rhombus / Diamond | Decision conditions, branching logic |
| `cylinder` | Storage drum | Databases, caches, file storage, data lakes |
| `text` | Frameless text block | Standalone annotations, notes, titles |

---

## Prerequisites & Installation

### Prerequisites

- **Python**: 3.12 or newer.
- **Package Manager**: [uv](https://docs.astral.sh/uv/) (recommended) or standard `pip`.
- **Supported Operating Systems**: Windows, Linux, macOS.

### Installation via uv (Recommended)

```bash
# Clone the repository
git clone https://github.com/manoj-025/sketchwright-mcp.git
cd sketchwright-mcp

# Install dependencies into isolated virtual environment
uv sync --all-groups
```

### Installation via pip

```bash
# Clone and install in editable mode with development dependencies
git clone https://github.com/manoj-025/sketchwright-mcp.git
cd sketchwright-mcp
python -m venv .venv
# Activate environment (POSIX: source .venv/bin/activate | Windows: .venv\Scripts\Activate.ps1)
pip install -e ".[dev]"
```

---

## Public Python API

Sketchwright exports a fully typed public Python API:

```python
from sketchwright import (
    generate_diagram,
    validate_diagram,
    layout_diagram,
    export_diagram,
    update_diagram,
    get_capabilities,
)

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

# 1. Generate full Excalidraw scene
result = generate_diagram(spec, output_path="architecture.excalidraw", overwrite=True)

print(f"Valid Scene: {result.validation.is_valid}")
print(f"Canvas Size: {result.laid_out.canvas_rect.width} x {result.laid_out.canvas_rect.height}")
print(f"Total Elements: {len(result.scene['elements'])}")
```

Expected output:
```text
Valid Scene: True
Canvas Size: 853.0 x 310.0
Total Elements: 7
```

See [`examples/hello_world.py`](./examples/hello_world.py) for a complete standalone runnable script.

---

## Command-Line Interface

Sketchwright provides the `sketchwright` executable (and module invocation via `python -m sketchwright`).

### Exit Code Policy

| Exit Code | Classification | Description |
| :--- | :--- | :--- |
| `0` | Success | Command completed successfully. |
| `2` | User / Validation Error | Schema validation failure, syntax error, or invalid CLI flag. |
| `1` | Internal / Filesystem Error | Unexpected runtime exception or filesystem access error. |

### Common Commands

```powershell
# Inspect version and CLI help
uv run sketchwright --version
uv run sketchwright --help

# Query runtime capabilities and limits
uv run sketchwright capabilities

# Validate a diagram specification or Excalidraw scene
uv run sketchwright validate examples/architecture.json
uv run sketchwright validate my_diagram.excalidraw

# Generate an Excalidraw scene file (.excalidraw)
uv run sketchwright generate examples/architecture.json -o web_arch.excalidraw --overwrite

# Generate an SVG file (.svg)
uv run sketchwright generate examples/flowchart.json -o flowchart.svg --format svg --overwrite

# Compute raw geometry and routing coordinates without writing a scene
uv run sketchwright layout examples/architecture.json --direction LR

# Launch the MCP server over standard input/output
uv run sketchwright mcp
```

Sample output from `uv run sketchwright validate examples/architecture.json`:
```text
Validation result for architecture.json: VALID
```

---

## MCP Server Integration

To register Sketchwright in an MCP client (such as Claude Desktop, VS Code, or Google Antigravity), add the following entry to your host's MCP configuration file (e.g., `mcpServers` object):

```json
{
  "mcpServers": {
    "sketchwright": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "<PATH_TO_SKETCHWRIGHT_MCP>",
        "sketchwright",
        "mcp"
      ]
    }
  }
}
```

> **Note:** Replace `<PATH_TO_SKETCHWRIGHT_MCP>` with the absolute path to your cloned `sketchwright-mcp` directory (use forward slashes `/` on all platforms).

### Registered MCP Tools

| Tool Name | Purpose | Key Parameters |
| :--- | :--- | :--- |
| `sketchwright_create_diagram` | Generates complete Excalidraw scene JSON from specification or text DSL. | `specification`, `text_dsl`, `layout_overrides`, `output_path`, `overwrite` |
| `sketchwright_update_diagram` | Incrementally mutates an existing specification (add/remove nodes, edges) and regenerates scene. | `specification`, `patch`, `generate_scene`, `output_path`, `overwrite` |
| `sketchwright_validate_diagram` | Validates a diagram specification or Excalidraw scene for schema conformance and bindings. | `specification`, `scene` |
| `sketchwright_layout_diagram` | Computes deterministic node coordinates, canvas bounds, and edge routes without serialization. | `specification`, `algorithm`, `direction` |
| `sketchwright_export_diagram` | Exports a diagram specification or scene to `.excalidraw` or `.svg`. | `specification`, `scene`, `format`, `output_path`, `overwrite` |
| `sketchwright_get_capabilities` | Returns machine-readable report of supported shapes, algorithms, directions, and limits. | None |

### Registered MCP Resources & Prompts

- **Resources**:
  - `schema://v1.0`: Canonical JSON Schema for `DiagramSpec`.
  - `capabilities://manifest`: Runtime capability and limits manifest.
  - `guide://usage`: Comprehensive prompt engineering guide and diagram patterns.
- **Prompts**:
  - `architecture_diagram`: Prompt guide for structured software architecture requests.
  - `flowchart_diagram`: Prompt guide for workflow/decision flowcharts.
  - `dependency_graph`: Prompt guide for software/package dependency graphs.

---

## Configuration

Sketchwright works out of the box with zero external configuration. Settings can be customized via environment variables (or a local `.env` file; see [`.env.example`](./.env.example)).

### Precedence Order

1. **Explicit API / CLI Argument / Tool Parameter** (highest precedence)
2. **Diagram Specification `layout` block**
3. **Environment Variables (`SKETCHWRIGHT_*`)**
4. **Internal Default Settings** (lowest precedence)

### Environment Variables

| Variable | Type | Default | Description | Secret |
| :--- | :--- | :--- | :--- | :--- |
| `SKETCHWRIGHT_LOG_LEVEL` | string | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`). | No |
| `SKETCHWRIGHT_DEFAULT_ALGORITHM` | string | `layered` | Default layout algorithm (`layered`, `grid`, `tree`). | No |
| `SKETCHWRIGHT_DEFAULT_DIRECTION` | string | `LR` | Default layout direction (`LR`, `RL`, `TB`, `BT`). | No |
| `SKETCHWRIGHT_NODE_SPACING` | float | `80.0` | Intra-rank spacing between adjacent nodes in pixels. | No |
| `SKETCHWRIGHT_RANK_SPACING` | float | `120.0` | Distance between consecutive ranks/layers in pixels. | No |
| `SKETCHWRIGHT_PADDING` | float | `40.0` | Outer canvas margin around diagram bounds in pixels. | No |
| `SKETCHWRIGHT_MAX_INPUT_BYTES` | int | `1048576` | Maximum allowed input payload size in bytes (1 MB). | No |
| `SKETCHWRIGHT_MAX_NODES` | int | `500` | Maximum number of nodes permitted per diagram. | No |
| `SKETCHWRIGHT_MAX_EDGES` | int | `1000` | Maximum number of edges permitted per diagram. | No |
| `SKETCHWRIGHT_MAX_LABEL_LENGTH` | int | `256` | Maximum permitted characters for any label. | No |
| `SKETCHWRIGHT_ALLOWED_DIR` | string | *unset* | Path boundary: restricts file outputs to an authorized root. | No |

---

## Canonical Specification Format

```json
{
  "schema_version": "1.0",
  "title": "Example Web Architecture",
  "layout": {
    "algorithm": "layered",
    "direction": "LR",
    "node_spacing": 80.0,
    "rank_spacing": 120.0,
    "padding": 40.0
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
  "groups": [
    { "id": "backend", "label": "Backend Tier", "node_ids": ["api", "database"] }
  ],
  "options": {
    "deterministic": true
  }
}
```

See [`docs/architecture/Schema.md`](./docs/architecture/Schema.md) for detailed schema specifications.

---

## Project Structure

Derived from verified repository source files:

```text
sketchwright-mcp/
├── .github/workflows/ci.yml       # Cross-platform GitHub Actions CI (Linux, Windows)
├── docs/                          # Comprehensive technical documentation suite
│   ├── README.md                  # Documentation suite index & master navigation map
│   ├── product/                   # PRD, user journeys, app flows, and terminology glossary
│   │   ├── PRD.md                 # Product Requirements Document
│   │   ├── AppFlow.md             # State inventory, CLI trees & MCP protocol lifecycles
│   │   └── Glossary.md            # Canonical terminology & domain dictionary
│   ├── architecture/              # Technical specs, design tokens, schemas, APIs & ADRs
│   │   ├── TechSpec.md            # System design, layout pipeline & C4 architecture
│   │   ├── Design.md              # Visual identity & Excalidraw styling tokens
│   │   ├── Schema.md              # Canonical specification & Pydantic data models
│   │   ├── API.md                 # FastMCP tool signatures & CLI contracts
│   │   └── decisions/             # Architecture Decision Records (ADRs)
│   ├── guides/                    # Operational runbooks, configurations & user handbooks
│   │   ├── configuration.md       # Environment variables & tuning limits
│   │   ├── Deployment.md          # Build, release, PyPI publishing & client configs
│   │   ├── troubleshooting.md     # Diagnostic procedures & error resolutions
│   │   └── SecurityAndCompliance.md # STRIDE threat model & security boundaries
│   └── development/               # Engineering standards, testing & code quality
│       ├── Rules.md               # Engineering guidelines & code quality standards
│       └── testing.md             # Test strategy, critical test cases & coverage
├── examples/                      # Runnable samples and test fixtures
│   ├── architecture.json          # Multi-tier microservice architecture spec
│   ├── flowchart.json             # Branching process flowchart spec
│   ├── hello_world.py             # Public Python API usage example
│   └── mcp-client-config.example.json # Generic MCP client host config
├── src/sketchwright/              # Core application package
│   ├── engine/                    # Diagram generator and update engine
│   ├── excalidraw/                # Excalidraw serializer, validator, and SVG export
│   ├── layout/                    # Sugiyama layout, geometry, and stepped routing
│   ├── mcp/                       # MCP 2.x server, tools, resources, and prompts
│   ├── models/                    # Pydantic v2 schemas and validation models
│   ├── parser/                    # Structured JSON and text DSL parsers
│   ├── cli.py                     # Command-line interface subcommands
│   ├── config.py                  # Settings and defensive limit management
│   └── logging_config.py          # Strict stdio/stderr routing
├── tests/                         # Multi-level automated test suite (91 tests)
│   ├── contract/                  # MCP protocol and tool discovery tests
│   ├── e2e/                       # Subprocess stdio integration tests
│   ├── integration/               # Pipeline execution and determinism tests
│   └── unit/                      # Unit tests for CLI, models, layout, and export
├── .env.example                   # Environment variable template
├── CHANGELOG.md                   # Version release notes (Keep a Changelog)
├── CONTRIBUTING.md                # Contribution guidelines and setup steps
├── LICENSE                        # MIT License
├── pyproject.toml                 # Package manifest and tool configuration
└── SECURITY.md                    # Vulnerability reporting and security architecture
```

---

## Testing & Verification

Sketchwright includes an automated test suite across unit, integration, contract, and end-to-end levels:

```bash
# Run the complete test suite (91 tests)
uv run pytest -v

# Run code style and formatting checks
uv run ruff check .
uv run ruff format --check .

# Run static type checking with Mypy in strict mode
uv run mypy src

# Validate package build
uv build
```

Observed test status: **91 passed in 4.19s** (100% pass rate).

---

## Known Limitations

1. **Approximate Font Metrics**: To avoid heavy binary font rendering dependencies (such as HarfBuzz or FreeType), Sketchwright computes bounding boxes using deterministic character width heuristics. Browser rendering in Excalidraw may show minor visual variations depending on locally installed fallback fonts.
2. **Simplified Edge Routing**: Orthogonal stepped routing avoids node interiors and handles backward loops; complex multi-hop obstacle avoidance routes around rank boundaries rather than sub-pixel collision routing.
3. **Manual Host Configuration**: MCP client hosts (Claude Desktop, VS Code, Antigravity) require manual registration by appending the server configuration block to their respective configuration files.

---

## Security Architecture

- **Strict Resource Bounds**: Limits input payloads to 1 MB (`SKETCHWRIGHT_MAX_INPUT_BYTES`), 500 nodes (`SKETCHWRIGHT_MAX_NODES`), 1000 edges (`SKETCHWRIGHT_MAX_EDGES`), and 256 characters per label (`SKETCHWRIGHT_MAX_LABEL_LENGTH`).
- **Filesystem Boundary Isolation**: File writes are executed atomically using temporary files followed by atomic replacement. Traversal sequences (`../`) are detected and rejected. Output directory restrictions can be enforced via `SKETCHWRIGHT_ALLOWED_DIR`.
- **Zero Dynamic Code Execution**: The codebase contains zero calls to `eval`, `exec`, or dynamic module loading.
- **Protocol Isolation**: Standard output (`stdout`) is strictly reserved for MCP JSON-RPC protocol messages; all application logs and diagnostics are directed exclusively to `stderr`.

For vulnerability disclosure procedures, see [`SECURITY.md`](./SECURITY.md).

---

## Contributing

Contributions are welcome. Please read [`CONTRIBUTING.md`](./CONTRIBUTING.md) for workflow instructions, code standards, and local quality check commands.

All pull requests must pass formatting (`ruff format`), linting (`ruff check`), static type analysis (`mypy src`), and the full test suite (`pytest -v`).

---

## License

Distributed under the **MIT License**. See [`LICENSE`](./LICENSE) for the full text.

Copyright (c) 2026 Sketchwright Contributors.
