"""Deterministic graph layout algorithms: Layered (Sugiyama) and Grid fallback."""

from __future__ import annotations

import math
from collections import defaultdict, deque

from sketchwright.layout.geometry import Rect, approximate_text_dimensions
from sketchwright.models.diagram import DiagramSpec
from sketchwright.models.elements import EdgeSpec, LayoutDirection, NodeSpec


class LayeredLayout:
    """Sugiyama-style deterministic layered layout algorithm.

    Handles cycles, disconnected components, self-loops, and multi-directional flows.
    """

    def __init__(self, spec: DiagramSpec) -> None:
        self.spec = spec
        self.direction: LayoutDirection = spec.layout.direction
        self.node_spacing = spec.layout.node_spacing
        self.rank_spacing = spec.layout.rank_spacing
        self.padding = spec.layout.padding

    def compute_positions(self) -> dict[str, Rect]:
        """Compute non-overlapping, deterministic positions for all nodes."""
        nodes = self.spec.nodes
        if not nodes:
            return {}

        # 1. Determine dimensions for each node
        node_sizes: dict[str, tuple[float, float]] = {}
        for n in nodes:
            w = n.width
            h = n.height
            if w is None or h is None:
                calc_w, calc_h = approximate_text_dimensions(
                    text=n.label or n.id,
                    font_size=self.spec.style.font_size,
                    shape=n.shape,
                )
                w = calc_w if w is None else w
                h = calc_h if h is None else h
            node_sizes[n.id] = (w, h)

        # 2. Partition into weakly connected components
        components = self._find_connected_components(nodes)

        # 3. Lay out each component independently
        component_rects: list[dict[str, Rect]] = []
        for comp_nodes in components:
            rects = self._layout_component(comp_nodes, node_sizes)
            component_rects.append(rects)

        # 4. Pack components side-by-side or stacked according to direction
        merged_positions = self._pack_components(component_rects)
        return merged_positions

    def _find_connected_components(self, nodes: list[NodeSpec]) -> list[list[NodeSpec]]:
        """Find weakly connected components using deterministic BFS."""
        node_map = {n.id: n for n in nodes}
        adj: dict[str, set[str]] = defaultdict(set)
        for e in self.spec.edges:
            if e.source in node_map and e.target in node_map and e.source != e.target:
                adj[e.source].add(e.target)
                adj[e.target].add(e.source)

        visited: set[str] = set()
        components: list[list[NodeSpec]] = []

        # Sort node keys for strict determinism
        sorted_ids = sorted(node_map.keys())
        for nid in sorted_ids:
            if nid in visited:
                continue
            comp_ids: list[str] = []
            queue = deque([nid])
            visited.add(nid)

            while queue:
                curr = queue.popleft()
                comp_ids.append(curr)
                for neighbor in sorted(adj[curr]):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)

            # Keep original spec order for nodes in component
            comp_nodes = [node_map[cid] for cid in sorted(comp_ids)]
            components.append(comp_nodes)

        return components

    def _layout_component(
        self,
        nodes: list[NodeSpec],
        node_sizes: dict[str, tuple[float, float]],
    ) -> dict[str, Rect]:
        """Lay out a single connected component using cycle-breaking, ranking, and crossing minimization."""
        comp_ids = {n.id for n in nodes}
        edges = [e for e in self.spec.edges if e.source in comp_ids and e.target in comp_ids and e.source != e.target]

        # Cycle removal: detect back-edges via DFS
        dag_edges = self._break_cycles(comp_ids, edges)

        # Rank assignment (longest path)
        ranks = self._assign_ranks(comp_ids, dag_edges)

        # Group nodes by rank
        rank_groups: dict[int, list[str]] = defaultdict(list)
        for nid, r in ranks.items():
            rank_groups[r].append(nid)

        # Order nodes within ranks to minimize crossings
        ordered_ranks = self._order_ranks(rank_groups, dag_edges)

        # Coordinate assignment
        return self._assign_coordinates(ordered_ranks, node_sizes)

    def _break_cycles(self, node_ids: set[str], edges: list[EdgeSpec]) -> list[tuple[str, str]]:
        """Remove cycles by identifying back-edges in DFS traversal and reversing them."""
        adj: dict[str, list[str]] = defaultdict(list)
        for e in edges:
            adj[e.source].append(e.target)

        # Sort for determinism
        for u in adj:
            adj[u].sort()

        # 0 = unvisited, 1 = in progress (ancestor), 2 = finished
        color: dict[str, int] = {nid: 0 for nid in node_ids}
        dag_edges: list[tuple[str, str]] = []

        def dfs(u: str) -> None:
            color[u] = 1
            for v in adj[u]:
                if color[v] == 1:
                    # Back-edge detected; reverse in DAG
                    dag_edges.append((v, u))
                elif color[v] == 0:
                    dag_edges.append((u, v))
                    dfs(v)
                else:
                    dag_edges.append((u, v))
            color[u] = 2

        for nid in sorted(node_ids):
            if color[nid] == 0:
                dfs(nid)

        return dag_edges

    def _assign_ranks(self, node_ids: set[str], dag_edges: list[tuple[str, str]]) -> dict[str, int]:
        """Assign topological layers using longest-path ranking."""
        in_deg: dict[str, int] = {nid: 0 for nid in node_ids}
        adj: dict[str, list[str]] = defaultdict(list)
        for u, v in dag_edges:
            adj[u].append(v)
            in_deg[v] += 1

        ranks: dict[str, int] = {nid: 0 for nid in node_ids}
        queue = deque([nid for nid in sorted(node_ids) if in_deg[nid] == 0])

        while queue:
            u = queue.popleft()
            curr_rank = ranks[u]
            for v in sorted(adj[u]):
                ranks[v] = max(ranks[v], curr_rank + 1)
                in_deg[v] -= 1
                if in_deg[v] == 0:
                    queue.append(v)

        return ranks

    def _order_ranks(
        self,
        rank_groups: dict[int, list[str]],
        dag_edges: list[tuple[str, str]],
    ) -> list[list[str]]:
        """Minimize edge crossings using the barycentric heuristic."""
        pred: dict[str, list[str]] = defaultdict(list)
        succ: dict[str, list[str]] = defaultdict(list)
        for u, v in dag_edges:
            succ[u].append(v)
            pred[v].append(u)

        max_rank = max(rank_groups.keys(), default=0)
        ordered: list[list[str]] = []

        # Initial order: sorted by ID
        for r in range(max_rank + 1):
            ordered.append(sorted(rank_groups.get(r, [])))

        # Forward pass: barycentric ordering based on predecessors
        for r in range(1, max_rank + 1):
            prev_order = {nid: i for i, nid in enumerate(ordered[r - 1])}
            barycenters: list[tuple[float, str]] = []
            for nid in ordered[r]:
                preds = [prev_order[p] for p in pred[nid] if p in prev_order]
                avg = sum(preds) / len(preds) if preds else 0.0
                barycenters.append((avg, nid))
            barycenters.sort()
            ordered[r] = [nid for _, nid in barycenters]

        return ordered

    def _assign_coordinates(
        self,
        ordered_ranks: list[list[str]],
        node_sizes: dict[str, tuple[float, float]],
    ) -> dict[str, Rect]:
        """Convert ranks into 2D coordinates according to configured direction."""
        rects: dict[str, Rect] = {}
        if not ordered_ranks:
            return rects

        is_horizontal = self.direction in ("LR", "RL")

        # Rank dimension (width if LR/RL, height if TB/BT)
        rank_breadths: list[float] = []
        rank_total_lengths: list[float] = []

        for rank_nodes in ordered_ranks:
            breadth = 0.0
            total_len = 0.0
            for nid in rank_nodes:
                w, h = node_sizes[nid]
                if is_horizontal:
                    breadth = max(breadth, w)
                    total_len += h
                else:
                    breadth = max(breadth, h)
                    total_len += w
            if rank_nodes:
                total_len += (len(rank_nodes) - 1) * self.node_spacing
            rank_breadths.append(breadth)
            rank_total_lengths.append(total_len)

        max_span = max(rank_total_lengths, default=0.0)

        # Compute rank offsets
        rank_coords: list[float] = [0.0]
        for i in range(1, len(ordered_ranks)):
            prev_breadth = rank_breadths[i - 1]
            rank_coords.append(rank_coords[-1] + prev_breadth + self.rank_spacing)

        # Place items within each rank centered along orthogonal axis
        for r_idx, rank_nodes in enumerate(ordered_ranks):
            r_coord = rank_coords[r_idx]
            r_span = rank_total_lengths[r_idx]
            intra_offset = (max_span - r_span) / 2.0

            curr_intra = intra_offset
            for nid in rank_nodes:
                w, h = node_sizes[nid]
                if is_horizontal:
                    x = r_coord
                    y = curr_intra
                    curr_intra += h + self.node_spacing
                else:
                    x = curr_intra
                    y = r_coord
                    curr_intra += w + self.node_spacing
                rects[nid] = Rect(round(x, 1), round(y, 1), w, h)

        # Invert if RL or BT
        if self.direction == "RL":
            max_x = max((r.right for r in rects.values()), default=0.0)
            for nid, r in rects.items():
                rects[nid] = Rect(round(max_x - r.right, 1), r.y, r.width, r.height)
        elif self.direction == "BT":
            max_y = max((r.bottom for r in rects.values()), default=0.0)
            for nid, r in rects.items():
                rects[nid] = Rect(r.x, round(max_y - r.bottom, 1), r.width, r.height)

        return rects

    def _pack_components(self, component_rects: list[dict[str, Rect]]) -> dict[str, Rect]:
        """Pack multiple component bounding boxes cleanly with separation spacing."""
        merged: dict[str, Rect] = {}
        if not component_rects:
            return merged

        current_offset_x = self.padding
        current_offset_y = self.padding
        is_horizontal = self.direction in ("LR", "RL")

        for comp in component_rects:
            if not comp:
                continue

            # Find local min bounds of component
            min_x = min(r.left for r in comp.values())
            min_y = min(r.top for r in comp.values())
            max_x = max(r.right for r in comp.values())
            max_y = max(r.bottom for r in comp.values())

            w = max_x - min_x
            h = max_y - min_y

            # Shift into canvas coordinates
            for nid, r in comp.items():
                shifted_x = r.x - min_x + current_offset_x
                shifted_y = r.y - min_y + current_offset_y
                merged[nid] = Rect(round(shifted_x, 1), round(shifted_y, 1), r.width, r.height)

            if is_horizontal:
                # Stack disconnected components vertically
                current_offset_y += h + self.rank_spacing
            else:
                # Stack disconnected components horizontally
                current_offset_x += w + self.rank_spacing

        return merged


class GridLayout:
    """Deterministic grid layout for un-directed, disconnected, or matrix-like structures."""

    def __init__(self, spec: DiagramSpec) -> None:
        self.spec = spec
        self.node_spacing = spec.layout.node_spacing
        self.padding = spec.layout.padding

    def compute_positions(self) -> dict[str, Rect]:
        nodes = self.spec.nodes
        if not nodes:
            return {}

        n_count = len(nodes)
        cols = max(1, math.ceil(math.sqrt(n_count)))

        rects: dict[str, Rect] = {}
        # Compute uniform cell size
        max_w = 120.0
        max_h = 60.0
        for n in nodes:
            cw, ch = approximate_text_dimensions(n.label or n.id, self.spec.style.font_size, n.shape)
            max_w = max(max_w, n.width or cw)
            max_h = max(max_h, n.height or ch)

        for idx, n in enumerate(sorted(nodes, key=lambda x: x.id)):
            r_idx = idx // cols
            c_idx = idx % cols
            x = self.padding + c_idx * (max_w + self.node_spacing)
            y = self.padding + r_idx * (max_h + self.node_spacing)
            rects[n.id] = Rect(round(x, 1), round(y, 1), max_w, max_h)

        return rects
