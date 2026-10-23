# Configuration & Limits

Sketchwright uses defensive defaults that require zero external configuration for standard usage. Runtime behavior can be tailored using environment variables.

## Supported Environment Variables

| Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `SKETCHWRIGHT_LOG_LEVEL` | string | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |
| `SKETCHWRIGHT_DEFAULT_ALGORITHM` | string | `layered` | Default layout algorithm (`layered`, `grid`, `tree`). |
| `SKETCHWRIGHT_DEFAULT_DIRECTION` | string | `LR` | Default layout direction (`LR`, `RL`, `TB`, `BT`). |
| `SKETCHWRIGHT_NODE_SPACING` | float | `80.0` | Intra-rank spacing between nodes (px). |
| `SKETCHWRIGHT_RANK_SPACING` | float | `120.0` | Distance between adjacent ranks/layers (px). |
| `SKETCHWRIGHT_PADDING` | float | `40.0` | Outer canvas margin around diagram bounds (px). |
| `SKETCHWRIGHT_MAX_INPUT_BYTES` | int | `1048576` | Maximum allowed input payload size in bytes (1 MB). |
| `SKETCHWRIGHT_MAX_NODES` | int | `500` | Maximum number of nodes permitted per diagram. |
| `SKETCHWRIGHT_MAX_EDGES` | int | `1000` | Maximum number of edges permitted per diagram. |
| `SKETCHWRIGHT_MAX_LABEL_LENGTH` | int | `256` | Maximum permitted characters for any node/edge label. |

## Precedence Order

When determining layout and generation options, Sketchwright applies settings in the following strict order of precedence:
1. **Explicit API / CLI Argument / Tool Parameter** (highest precedence).
2. **Diagram Specification `layout` block**.
3. **Environment Variables (`SKETCHWRIGHT_*`)**.
4. **Internal Default Settings** (lowest precedence).
