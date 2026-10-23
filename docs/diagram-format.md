# Canonical Diagram Format Specification

Version: `1.0`

Sketchwright accepts both structured JSON specifications and a lightweight line-based DSL.

## 1. JSON Specification Schema

### Top-Level Properties

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `schema_version` | string | Yes | Format version (must be `"1.0"`). |
| `title` | string | No | Optional human-readable diagram title. |
| `layout` | object | No | Layout algorithm and geometry options. |
| `style` | object | No | Visual theme and styling. |
| `nodes` | array | Yes | List of node specifications. |
| `edges` | array | No | List of edge specifications. |
| `options` | object | No | Generation options (`deterministic: true`). |

### Node Specification (`NodeSpec`)

| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `id` | string | (required) | Unique node identifier (1-128 chars). |
| `label` | string | `""` | Text label displayed inside node. |
| `shape` | string | `"rectangle"` | Supported: `rectangle`, `rounded_rectangle`, `ellipse`, `diamond`, `cylinder`, `text`. |
| `width` | float | auto | Explicit width in px (calculated if omitted). |
| `height` | float | auto | Explicit height in px (calculated if omitted). |
| `group` | string | null | Optional group identifier. |

### Edge Specification (`EdgeSpec`)

| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `id` | string | (required) | Unique edge identifier. |
| `source` | string | (required) | Source node ID (must exist). |
| `target` | string | (required) | Target node ID (must exist). |
| `label` | string | null | Optional text label positioned along route. |
| `kind` | string | `"directed"` | `directed`, `undirected`, `bidirectional`. |

---

## 2. Textual DSL Specification

For quick diagram authoring without JSON boilerplate, Sketchwright provides a deterministic DSL parser:

```
# Title and direction directives
title: Order Processing Flow
direction: LR
algorithm: layered

# Node definitions: [id: shape: label]
[client: rectangle: Web Client]
[gateway: rounded_rectangle: API Gateway]
[orders: rectangle: Order Service]
[db: cylinder: Postgres DB]

# Edges: source -> target: label
client -> gateway: POST /order
gateway -> orders: gRPC
orders -> db: INSERT
orders --> client: 201 Created
```
