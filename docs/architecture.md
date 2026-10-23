# Architecture Overview

Sketchwright is structured as a decoupled, layered Python library with strict module boundaries. Protocol transport, CLI interactions, domain modeling, graph layout, and scene serialization are completely separated.

```
                    +---------------------------+
                    |   MCP Client / LLM Host   |
                    +-------------+-------------+
                                  |
                                  v
+-------------------+   +--------------------+   +-------------------+
|   CLI Terminal    |   |  MCP Server Layer  |   | Python Public API |
| (sketchwright.cli)|   | (mcp.server/tools) |   |   (generate_*)    |
+---------+---------+   +---------+----------+   +---------+---------+
          |                       |                        |
          +-----------------------+------------------------+
                                  |
                                  v
                    +---------------------------+
                    | Parser & Validation Layer |
                    | (DiagramSpec / Pydantic)  |
                    +-------------+-------------+
                                  |
                                  v
                    +---------------------------+
                    |  Deterministic Layout     |
                    | (Sugiyama Layered / Grid) |
                    +-------------+-------------+
                                  |
                                  v
                    +---------------------------+
                    |  Excalidraw Serialization |
                    |   (Bindings & Elements)   |
                    +-------------+-------------+
                                  |
                                  v
                    +---------------------------+
                    | Scene Validator & Export  |
                    | (.excalidraw / .svg)      |
                    +---------------------------+
```

## Subsystems

### 1. Domain Models (`src/sketchwright/models`)
- Implements `DiagramSpec`, `NodeSpec`, `EdgeSpec`, `LayoutConfig`, and `StyleConfig` using Pydantic.
- Performs semantic validation: checks node uniqueness, edge endpoint validity, finite coordinates, and resource limits.

### 2. Parser Layer (`src/sketchwright/parser`)
- `structured.py`: Decodes JSON with input byte-size limits to protect against payload exhaustion.
- `text.py`: Deterministic line-based DSL parser for rapid flowchart and pipeline authoring.

### 3. Layout Engine (`src/sketchwright/layout`)
- `geometry.py`: 2D primitives (`Point`, `Rect`), ray-shape intersection algorithms, and approximate font metrics.
- `algorithms.py`: Sugiyama layered layout implementation:
  - Cycle breaking via DFS 3-color back-edge detection.
  - Longest-path topological ranking.
  - Barycentric heuristic crossing minimization.
  - Direction transforms (`LR`, `RL`, `TB`, `BT`).
  - Disconnected component partitioning and packing.
- `routing.py`: Orthogonal stepped routing, self-loop curving, and label positioning with clearance.

### 4. Excalidraw Adapter (`src/sketchwright/excalidraw`)
- `bindings.py`: Deterministic stable element ID generation using salted SHA-256; reciprocal binding management.
- `serializer.py`: Converts laid-out diagrams into official Excalidraw v2 scene documents.
- `validator.py`: Verifies structural integrity, binding targets, and geometry sanity.
- `export.py`: Atomic file writing and standalone SVG rendering.

### 5. MCP Integration (`src/sketchwright/mcp`)
- Built on the official `mcp 2.3.0` Python SDK.
- Exposes tools, resources, and prompt templates.
- Enforces strict stdio discipline: all diagnostic logs go to `stderr`, keeping `stdout` reserved for JSON-RPC frames.
