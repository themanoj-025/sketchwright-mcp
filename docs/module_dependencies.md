# Module Dependencies & Graph Integrity

The module import graph is strictly unidirectional:
`Interfaces (cli, mcp)` -> `Engine` -> `Parser/Models` -> `Layout` -> `Excalidraw Output`.

- **Total Internal Modules**: 29
- **Circular Import Cycles**: 0 (Verified via `BP-21` & Gate `G05`)
- **Third-Party Dependencies**: `mcp >= 2.3.0`, `pydantic >= 2.14.0`
