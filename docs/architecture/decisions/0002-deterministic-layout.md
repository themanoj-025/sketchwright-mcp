# ADR 0002: Pure Python Deterministic Sugiyama Layout Engine

## Context
Diagram layout requires assigning coordinates to nodes and routing edges. While tools like Graphviz exist, they require platform-specific C binaries (`dot`) which introduce installation friction, security concerns with untrusted inputs, and cross-platform inconsistencies (particularly on Windows).

## Decision
We implement a zero-dependency, pure Python Sugiyama layered layout engine in `sketchwright.layout`:
1. **Cycle Breaking**: DFS 3-color back-edge detection condenses cyclic graphs into DAGs for ranking, then restores original directions.
2. **Topological Ranking**: Longest-path ranking assigns nodes to discrete layers.
3. **Crossing Reduction**: Iterative barycentric heuristic orders nodes within ranks.
4. **Coordinate Normalization**: Geometry is scaled and centered according to flow direction (`LR`, `RL`, `TB`, `BT`).
5. **Stable Hashing**: Element IDs use salted SHA-256 instead of Python's randomized `hash()`.

## Consequences
- Guaranteed deterministic outputs: repeated runs produce identical numeric coordinates and byte-identical JSON.
- 100% pure Python with zero external binary dependencies.
- Reliable cross-platform execution on Windows, Linux, and macOS.
