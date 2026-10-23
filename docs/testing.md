# Testing Strategy & Verification Suite

Sketchwright implements an automated verification strategy across four test tiers: unit, integration, contract, and end-to-end.

## Running Tests

```powershell
# Run the complete test suite
uv run pytest -v

# Run with test coverage report (if pytest-cov installed)
uv run pytest --cov=sketchwright tests/
```

## Test Tiers

### 1. Unit Tests (`tests/unit/`)
- `test_models.py`: Validates Pydantic specifications, unique ID enforcement, resource limits, and finite numeric bounds.
- `test_parser.py`: Tests JSON string/file decoding, payload size limits, and line-based text DSL parsing.
- `test_geometry.py`: Verifies `Point`, `Rect`, ray-shape perimeter anchors, and text sizing heuristics.
- `test_layout.py`: Verifies Sugiyama ranking, cycle breaking termination, multi-directional flow, and grid fallback.
- `test_serializer.py`: Verifies Excalidraw element properties, reciprocal container bindings, and arrow bindings.
- `test_validator.py`: Tests scene validator against structural defects, dangling references, and non-finite coordinates.
- `test_export.py`: Tests atomic file writing, overwrite protection, and standalone SVG generation.
- `test_cli.py`: Verifies CLI arguments, help text, version output, and documented exit codes (0, 1, 2).

### 2. Integration Tests (`tests/integration/`)
- `test_pipeline.py`: Runs full pipeline across representative fixtures (architecture, flowchart, cyclic state machine, disconnected clusters, unicode characters) and verifies scene validity.
- `test_determinism.py`: Asserts that repeated generation runs produce byte-for-byte and semantically identical outputs.

### 3. Contract Tests (`tests/contract/`)
- `test_mcp_server.py`: Uses the official `mcp.server.mcpserver.MCPServer` in-process interface to verify:
  - Tool discovery for all 5 tools (`create_diagram`, `validate_diagram`, `layout_diagram`, `export_diagram`, `get_capabilities`).
  - Correct argument schemas and structured responses.
  - Resource listings (`schema://v1.0`, `capabilities://manifest`).
  - Prompt templates (`architecture_diagram`, `flowchart_diagram`).

### 4. End-to-End Tests (`tests/e2e/`)
- `test_subprocess_mcp.py`: Launches `sketchwright mcp` in a live subprocess, performs a real JSON-RPC `initialize` handshake over stdio, and verifies that stdout is strictly reserved for protocol frames.
