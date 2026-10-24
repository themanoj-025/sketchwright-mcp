| Field | Value |
|---|---|
| Version | v1.0.0 |
| Last Updated | 2026-10-24 |
| Owner | Lead Design Architect |
| Status | Approved |

# 📄 Design System & Visual Specification (Design) — Sketchwright

## 1. Design Principles

### Principle 1: Deterministic Visual Harmony
- **Rationale**: Diagrams must look deliberately hand-crafted rather than mechanically jammed together.
- **Do**: Enforce strict minimum padding, consistent rank spacing (120px), and clear orthogonal clearances.
- **Don't**: Overlap shape boundaries or allow text to escape beyond its container.

### Principle 2: Semantic Color Utility
- **Rationale**: Colors must convey architectural intent (databases vs services vs clients), not mere decoration.
- **Do**: Assign curated pastels and distinct strokes to functional system layers.
- **Don't**: Use uncurated raw RGB primaries or arbitrary rainbow fills across similar node types.

### Principle 3: Authentic Hand-Drawn Fidelity
- **Rationale**: Generated scenes must blend seamlessly into native Excalidraw canvases.
- **Do**: Use Excalidraw's `roughness=1`, `fontFamily=1` (Virgil/hand-drawn), and subtle slop offsets.
- **Don't**: Inject rigid, computer-perfect CAD vectors that look alien inside Excalidraw.

### Principle 4: High Contrast Accessibility (WCAG 2.1 AA)
- **Rationale**: Architecture diagrams must remain easily readable in low-contrast projectors and dark modes.
- **Do**: Maintain at least a 4.5:1 contrast ratio between label text and background fills.
- **Don't**: Place dark gray text on medium gray or saturated blue backgrounds.

## 2. Visual Identity & Theme
Sketchwright targets the official **Excalidraw v2 scene specification**. The aesthetic is defined by casual hand-drawn lines, rounded polyline vertices, Virgil typography, and subtle cross-hatch or solid pastel fills.

```
+-------------------------------------------------------------+
| Frame / System Boundary (Stroke: #1e1e1e, Dash: dashed)     |
|                                                             |
|   +-----------------------+         +-------------------+   |
|   | Microservice Component| ------> | PostgreSQL DB     |   |
|   | Fill: #e3fafc (Solid) |         | Fill: #ebfbee     |   |
|   | Stroke: #1e1e1e       |         | Shape: cylinder   |   |
|   +-----------------------+         +-------------------+   |
+-------------------------------------------------------------+
```

## 3. Color System & Palette Tokens

All colors are checked against WCAG 2.1 AA contrast requirements against standard `#ffffff` (light mode) and `#121212` (dark mode) backgrounds.

| Token Name | Hex Code | Purpose / Semantic Role | Contrast vs `#ffffff` | Contrast vs `#121212` |
|---|---|---|:---:|:---:|
| `color-canvas-bg` | `#ffffff` | Default Excalidraw canvas background | N/A | 21.0:1 |
| `color-canvas-dark` | `#121212` | Dark mode canvas background | 21.0:1 | N/A |
| `color-stroke-primary` | `#1e1e1e` | Primary border stroke and edge lines | 16.1:1 | 1.3:1 (invert in dark) |
| `color-stroke-muted` | `#868e96` | Secondary boundary frames and grid markers | 3.5:1 | 4.6:1 |
| `color-text-primary` | `#1e1e1e` | Node labels and primary edge annotations | 16.1:1 | 1.3:1 (invert in dark) |
| `color-fill-blue` | `#e7f5ff` | Frontend clients, web apps, API gateways | 1.1:1 | 18.2:1 |
| `color-fill-green` | `#ebfbee` | Microservices, compute workers, handlers | 1.1:1 | 17.8:1 |
| `color-fill-yellow` | `#fff9db` | Caches, message queues, buffers | 1.1:1 | 19.5:1 |
| `color-fill-red` | `#ffe3e3` | External third-party APIs, untrusted zones | 1.2:1 | 16.4:1 |
| `color-fill-violet` | `#f3f0ff` | Databases, persistent storage, data lakes | 1.1:1 | 17.5:1 |
| `color-fill-gray` | `#f8f9fa` | Generic fallback components | 1.05:1 | 19.8:1 |

## 4. Typography Scale

Excalidraw utilizes font families: `1` (Virgil / Hand-drawn), `2` (Helvetica / Normal), `3` (Cascadia / Monospace). Sketchwright defaults to Virgil (`1`) for hand-drawn consistency.

| Typography Token | Font Family | Size (px) | Weight | Line Height | Usage Context |
|---|---|:---:|---|:---:|---|
| `font-title` | Virgil (`1`) | `28px` | Bold / Heavy | `1.2` | Frame titles, diagram header labels |
| `font-node-primary` | Virgil (`1`) | `20px` | Normal | `1.25` | Primary node labels (services, databases) |
| `font-node-secondary` | Virgil (`1`) | `16px` | Normal | `1.2` | Subtitle descriptions, technology tags |
| `font-edge-label` | Virgil (`1`) | `14px` | Normal | `1.15` | Action verbs on connecting edges (`submits`, `reads`) |
| `font-code` | Cascadia (`3`) | `14px` | Monospace | `1.3` | Endpoint paths, port numbers (`:8080`), code snippets |

## 5. Spacing, Dimensions & Grid System

Sketchwright applies an internal layout grid system based on an **8px base unit**:

| Spacing Token | Value | Purpose |
|---|:---:|---|
| `grid-base` | `8px` | Atomic coordinate alignment quantum |
| `node-min-width` | `120px` | Minimum width for simple rectangular shapes |
| `node-min-height` | `60px` | Minimum height for simple single-line nodes |
| `node-padding-x` | `16px` | Horizontal text clearance inside container |
| `node-padding-y` | `12px` | Vertical text clearance inside container |
| `default-node-spacing` | `80px` | Horizontal/vertical gap between adjacent nodes in the same rank |
| `default-rank-spacing` | `120px` | Separation between hierarchical Sugiyama layers |
| `frame-padding` | `40px` | Padding between boundary frame border and enclosed child nodes |
| `edge-label-clearance` | `10px` | Margin between polyline edge stroke and floating label box |

## 6. Component Shape Library & Anatomy

### 6.1 Node Shape Anatomy
```
      +------------- node-min-width: 120px -------------+
      |                                                 |
  +---v-------------------------------------------------v---+ ---
  |   (node-padding-y: 12px)                                |  |
  |   +-------------------------------------------------+   |  |
  |   |           Primary Label (font: 20px)            |   |  node-min-height: 60px
  |   +-------------------------------------------------+   |  |
  |   (node-padding-y: 12px)                                |  |
  +---------------------------------------------------------+ ---
      |<- node-padding-x: 16px ->|
```

### 6.2 Supported Element Shapes
| Shape Type | Excalidraw Element | Default Dimensions | Common Semantic Usage |
|---|---|:---:|---|
| `rectangle` | `rectangle` (`roundness: null`) | `140 x 70` | Generic process, function, step |
| `rounded_rectangle` | `rectangle` (`roundness: {type: 3}`) | `140 x 70` | Microservice, application, API controller |
| `ellipse` | `ellipse` | `100 x 100` | Start/end states, event triggers, users |
| `diamond` | `diamond` | `100 x 100` | Decision branches, conditional routers, gates |
| `cylinder` | Custom cylinder polyline/ellipse | `120 x 80` | Databases, key-value stores, disk storage |
| `frame` | `frame` | Dynamic enclosure | Grouping subsystems, VPCs, network zones |
| `arrow` | `arrow` (`roundness: {type: 2}`) | Dynamic polyline | Data flow, HTTP calls, asynchronous events |

## 7. Directional Spatial Behavior
Sketchwright supports four primary layout directions via `LayoutDirection`:
- **`LR` (Left-to-Right, Default)**: Ideal for sequential pipelines, auth flows, and data ingestion architectures.
- **`TB` (Top-to-Bottom)**: Ideal for hierarchical organizational trees, database schema relationships, and call stacks.
- **`RL` (Right-to-Left)**: Used for bidirectional flows and inverted pipelines.
- **`BT` (Bottom-to-Top)**: Used for dependency injection graphs and infrastructure stack layers.

## 8. Accessibility & Color Blindness Defenses
1. **Multi-Signal Identification**: Nodes never rely solely on color to indicate type; shape geometry (`cylinder` vs `rectangle` vs `diamond`) and explicit textual subtitles indicate semantic roles.
2. **Text Background Knockouts**: Edge labels feature semi-opaque white bounding boxes (`#ffffff` with `opacity=0.85`) to ensure connecting arrow strokes never obscure text characters.

## 9. Related Documents
| Document | Relationship & Cross-Reference |
|---|---|
| [PRD.md](file:///f:/GITHUB/sketchwright-mcp/docs/PRD.md) | User personas and functional requirements. |
| [TechSpec.md](file:///f:/GITHUB/sketchwright-mcp/docs/TechSpec.md) | Architectural layout engine and serializer implementations. |
| [AppFlow.md](file:///f:/GITHUB/sketchwright-mcp/docs/AppFlow.md) | Application states and visual diagram presentations. |
| [Schema.md](file:///f:/GITHUB/sketchwright-mcp/docs/Schema.md) | Element attributes, color property types, and geometry fields. |
| [Testing.md](file:///f:/GITHUB/sketchwright-mcp/docs/Testing.md) | Visual regression testing and coordinate determinism validation. |
