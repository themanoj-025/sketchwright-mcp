# Layout Engine Architecture & Invariants

Sketchwright features a built-in deterministic layout engine designed to produce clean, legible, non-overlapping diagrams without external graphviz dependencies.

## 1. Sugiyama Layered Algorithm

The layered layout algorithm runs in four deterministic phases:

### Phase 1: Cycle Breaking (Feedback Edge Set)
- Cyclic graphs are analyzed using Depth-First Search with 3-color node classification (`WHITE`, `GRAY`, `BLACK`).
- Any edge pointing to an ancestor currently active on the recursion stack (`GRAY`) is identified as a back-edge.
- In the DAG representation used for ranking, back-edges are reversed to guarantee topological termination.

### Phase 2: Layer / Rank Assignment
- Topological in-degrees are calculated on the DAG.
- Longest-path ranking assigns each node a layer index:
  $$\text{rank}(v) = \max_{(u, v) \in E} (\text{rank}(u) + 1)$$
- Nodes with 0 in-degrees are placed in rank 0.

### Phase 3: Crossing Minimization (Barycentric Heuristic)
- Within each rank $r > 0$, nodes are sorted based on the average index position of their predecessors in rank $r - 1$:
  $$\text{barycenter}(v) = \frac{1}{|\text{pred}(v)|} \sum_{u \in \text{pred}(v)} \text{order}(u)$$
- Tie-breaking is performed deterministically using alphabetical node ID order.

### Phase 4: Coordinate Assignment & Centering
- Based on the layout direction (`LR`, `RL`, `TB`, `BT`):
  - Ranks determine progression along the primary axis.
  - Intra-rank order determines progression along the orthogonal axis.
  - Shorter ranks are centered along the median canvas axis so columns/rows appear balanced.

---

## 2. Edge Routing

- **Orthogonal Stepped Routing**: For forward progressive edges, routes exit the source shape boundary anchor, step horizontally/vertically to the rank midpoint, and enter the target shape anchor.
- **Backward Loop Routing**: Cyclic or feedback edges route around the outer bounding box of intermediate nodes with clearance.
- **Self-Loops**: Edges where `source == target` curl around the upper-right corner of the node in a 4-point arc.
- **Parallel Edge Offsetting**: Multiple edges sharing endpoints receive incremental perpendicular offsets to avoid visual collision.

---

## 3. Layout Invariants

- **Non-Overlap Guarantee**: Ungrouped nodes in the same rank and across adjacent ranks are guaranteed non-overlapping when using `node_spacing >= 50` and `rank_spacing >= 80`.
- **Termination Guarantee**: Cyclic graphs terminate in linear-time $O(V + E)$ without infinite loops or stack overflow.
- **Deterministic Coordinates**: Identical input specifications always yield identical numeric coordinates and identical element ordering.
