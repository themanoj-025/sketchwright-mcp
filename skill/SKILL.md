---
name: sketchwright-diagrams
description: Deterministic Excalidraw diagram generator, layout engine, and Model Context Protocol (MCP) server for software architecture, system topologies, microservices, flowcharts, and SVG export. Use whenever designing, generating, validating, or updating editable .excalidraw diagrams or SVGs.
---

# Sketchwright: Excalidraw Diagram Engine & MCP Skill

Generate deterministic, visually balanced, and fully editable **Excalidraw (`.excalidraw`)** diagram scenes and standalone **SVGs** directly from your AI agent.

Sketchwright separates **intent** from **geometry**: the AI determines *what* components and connections exist, while Sketchwright's Sugiyama layered layout engine deterministically computes *where* boxes, centered text containers, and reciprocal arrow bindings belong without manual pixel alignment or overlapping boxes.

---

## When to Use This Skill

Activate this skill whenever the user asks to:
- Create, design, or visualize **software architectures** (e.g., frontend, API gateway, microservices, databases, caches).
- Draw **system topologies or cloud infrastructure** (AWS, GCP, Azure, Kubernetes pods, queues).
- Generate **process flowcharts, CI/CD pipelines, or decision trees**.
- Create or export **`.excalidraw`** or **`.svg`** diagram files.
- Iteratively update, add nodes/edges to, or modify an existing diagram.

---

## MCP Server Setup

If the `sketchwright` MCP tools are not yet active in your agent environment, add this entry to your host's MCP configuration file (e.g., `claude_desktop_config.json`, `~/.cursor/mcp.json`, or your agent's MCP settings):

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

*(Alternatively, if running locally from the cloned repository:)*
```json
{
  "mcpServers": {
    "sketchwright": {
      "command": "uv",
      "args": ["run", "sketchwright", "mcp"]
    }
  }
}
```

---

## Available MCP Tools

### 1. `sketchwright_create_diagram`
The primary tool to create diagrams. Accepts either a structured JSON `specification` or a concise `text_dsl`.

* **Parameters:**
  * `specification` *(object, optional)*: Full `DiagramSpec` object (recommended for complex systems).
  * `text_dsl` *(string, optional)*: Plain-text diagram DSL (recommended for rapid single-turn diagrams).
  * `output_path` *(string, optional)*: Path where the resulting file should be written (e.g. `architecture.excalidraw`).
  * `overwrite` *(boolean, default `false`)*: Set to `true` to overwrite existing files.

### 2. `sketchwright_update_diagram`
Applies an incremental patch to an existing diagram specification without having to re-declare the whole graph.

* **Parameters:**
  * `specification` *(object)*: Existing diagram spec.
  * `patch` *(object)*: Mutations: `add_nodes`, `remove_nodes`, `add_edges`, `remove_edges`, `update_nodes`.
  * `output_path` *(string, optional)*: Target file path.
  * `overwrite` *(boolean)*: Overwrite permission.

### 3. `sketchwright_export_diagram`
Converts or exports a diagram or scene to `.excalidraw` or `.svg`.

* **Parameters:**
  * `specification` or `scene` *(object)*
  * `format` *(string)*: `"excalidraw"` or `"svg"`
  * `output_path` *(string)*: Output file path.

### 4. `sketchwright_validate_diagram`
Validates schema compliance, checks node IDs, and ensures all edge sources and targets exist.

### 5. `sketchwright_get_capabilities`
Returns active runtime limits, supported shapes, and layout algorithms.

---

## Diagram Specification Formats

You can define diagrams using **Text DSL** or **JSON Specification**.

### Option A: Lightweight Text DSL (Fastest)

Pass as `text_dsl`:

```text
title: Cloud Microservices Architecture
direction: LR
algorithm: layered

# Define Nodes: [id: shape: label]
[client: rounded_rectangle: Client App (Web / Mobile)]
[gateway: rectangle: API Gateway]
[auth: rectangle: Auth Service]
[orders: rectangle: Orders Microservice]
[inventory: rectangle: Inventory Microservice]
[db_users: cylinder: PostgreSQL (Users)]
[db_orders: cylinder: PostgreSQL (Orders)]
[queue: rounded_rectangle: RabbitMQ / Kafka]

# Define Edges: source -> target: label
client -> gateway: HTTPS / GraphQL
gateway -> auth: Verify Token
gateway -> orders: Place Order
gateway -> inventory: Check Stock
auth -> db_users: Read Credentials
orders -> db_orders: Write Transactions
orders -> queue: OrderCreated Event
queue -> inventory: Update Stock
```

### Option B: Structured JSON Specification

Pass as `specification`:

```json
{
  "schema_version": "1.0",
  "title": "Data Pipeline Architecture",
  "layout": {
    "algorithm": "layered",
    "direction": "LR"
  },
  "nodes": [
    {"id": "source", "label": "External Events API", "shape": "rounded_rectangle"},
    {"id": "ingest", "label": "Ingestion Lambda", "shape": "rectangle"},
    {"id": "queue", "label": "SQS Queue", "shape": "rounded_rectangle"},
    {"id": "processor", "label": "Stream Processor", "shape": "rectangle"},
    {"id": "warehouse", "label": "BigQuery Warehouse", "shape": "cylinder"}
  ],
  "edges": [
    {"id": "e1", "source": "source", "target": "ingest", "label": "Webhook"},
    {"id": "e2", "source": "ingest", "target": "queue", "label": "Batch Enqueue"},
    {"id": "e3", "source": "queue", "target": "processor", "label": "Poll 100/s"},
    {"id": "e4", "source": "processor", "target": "warehouse", "label": "Parquet Write"}
  ]
}
```

---

## Supported Shapes & Layout Rules

| Shape Identifier | Visual Appearance | Typical Use Case |
| :--- | :--- | :--- |
| `rectangle` | Sharp container | Services, modules, UI, backends |
| `rounded_rectangle` | Rounded container | Endpoints, queues, workers, terminals |
| `ellipse` | Circle / Oval | Start / stop states, events |
| `diamond` | Rhombus | Decision gates, condition checks, routers |
| `cylinder` | Storage drum | Databases, caches, object storage, data lakes |
| `text` | Frameless text | Annotations, titles, section notes |

### Flow Directions
- `LR` (Left-to-Right): Best for web architectures, microservices, and event streams.
- `TB` (Top-to-Bottom): Best for decision trees, hierarchical systems, and flowcharts.
- `RL` (Right-to-Left) and `BT` (Bottom-to-Top) are also fully supported.

---

## Best Practices for Agent Interactions

1. **Always provide an `output_path`**: Write directly to `<name>.excalidraw` in the user's workspace so they can immediately open or import it into [excalidraw.com](https://excalidraw.com) or the VS Code Excalidraw extension.
2. **Set `overwrite: true`** when iterating on an existing diagram.
3. **Use semantic shapes**: Reserve `cylinder` for data stores, `diamond` for decision logic, and `rounded_rectangle` for queues/gateways.
4. **Group related services**: When drawing multi-tier architectures, name node IDs with clear prefixes (e.g. `svc_auth`, `db_auth`) for clarity.

