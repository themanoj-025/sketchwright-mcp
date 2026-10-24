# 0003. PyPI Naming Verification, Incremental Updates, and Grouping

Date: 2026-10-23
Status: Accepted

## Context
1. Section 1.2 of the project specification mandates performing a real availability check on PyPI before declaring the Python distribution name, ensuring that `sketchwright` and `sketchwright-mcp` are available without conflicts.
2. Section 8 and 8.1 require supporting visual grouping and deterministic incremental diagram updates (addition, modification, renaming, removal with edge pruning, and ambiguous label rejection).

## Decision
1. **PyPI Availability**:
   - An active network check was executed against the official PyPI JSON API:
     - `https://pypi.org/pypi/sketchwright/json` returned HTTP 404 (Available).
     - `https://pypi.org/pypi/sketchwright-mcp/json` returned HTTP 404 (Available).
   - The primary distribution and package name is declared as `sketchwright`.
2. **Incremental Updates**:
   - Implemented in `src/sketchwright/engine/updater.py` with `update_diagram_spec`.
   - Priority matching is done via stable node ID, with a fallback to node label matching only if unambiguous (raising `ValidationError` when multiple nodes match).
   - Removing a node automatically cascades to prune dangling edges.
   - All unrelated elements, styles, and layout settings are preserved.
   - Post-update verification re-checks the complete scene schema and arrow bindings.
3. **Visual Grouping**:
   - Member nodes carry their group's stable ID in their `groupIds` array.
   - The serializer computes the bounding box for all member nodes in each declared group and emits a dashed rounded boundary rectangle behind the nodes with a group label.

## Consequences
- Guaranteed clean installation namespace on PyPI without collisions.
- AI hosts can iteratively refine diagrams through `sketchwright_update_diagram` or the public Python API `update_diagram`.
