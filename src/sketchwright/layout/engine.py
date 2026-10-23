"""Central layout engine coordinating algorithms, routing, and canvas geometry."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from sketchwright.errors import LayoutError
from sketchwright.layout.algorithms import GridLayout, LayeredLayout
from sketchwright.layout.geometry import Point, Rect
from sketchwright.layout.routing import EdgeRoute, route_edges
from sketchwright.models.diagram import DiagramSpec
from sketchwright.models.elements import ShapeType


@dataclass
class LaidOutNode:
    """A node positioned and sized on the canvas."""

    id: str
    rect: Rect
    shape: ShapeType
    label: str
    group: Optional[str] = None


@dataclass
class LaidOutDiagram:
    """A completely laid out diagram with computed node coordinates, routes, and canvas bounding box."""

    nodes: dict[str, LaidOutNode]
    edges: list[EdgeRoute]
    canvas_rect: Rect
    stats: dict[str, Any] = field(default_factory=dict)


class LayoutEngine:
    """Orchestrates deterministic graph layout calculations."""

    def __init__(self, spec: DiagramSpec) -> None:
        self.spec = spec

    def layout(self) -> LaidOutDiagram:
        """Execute deterministic layout and edge routing."""
        spec = self.spec
        algorithm = spec.layout.algorithm

        # 1. Compute node positions
        if algorithm == "layered":
            layout_algo = LayeredLayout(spec)
            positions = layout_algo.compute_positions()
        elif algorithm == "grid":
            layout_algo = GridLayout(spec)  # type: ignore[assignment]
            positions = layout_algo.compute_positions()
        elif algorithm == "tree":
            # Hierarchical tree uses layered algorithm with TB direction if not overridden
            layout_algo = LayeredLayout(spec)
            positions = layout_algo.compute_positions()
        else:
            raise LayoutError(
                f"Unsupported layout algorithm: '{algorithm}'. Supported algorithms: layered, grid, tree.",
                details={"algorithm": algorithm},
            )

        # 2. Check node overlaps
        overlaps: list[tuple[str, str]] = []
        node_ids = list(positions.keys())
        for i in range(len(node_ids)):
            for j in range(i + 1, len(node_ids)):
                id1, id2 = node_ids[i], node_ids[j]
                if positions[id1].intersects(positions[id2], tolerance=1.0):
                    overlaps.append((id1, id2))

        # 3. Route edges
        routes = route_edges(spec, positions)

        # 4. Construct laid out nodes
        node_map: dict[str, LaidOutNode] = {}
        for n in spec.nodes:
            if n.id in positions:
                node_map[n.id] = LaidOutNode(
                    id=n.id,
                    rect=positions[n.id],
                    shape=n.shape,
                    label=n.label or n.id,
                    group=n.group,
                )

        # 5. Compute global canvas bounding box
        all_pts: list[Point] = []
        for r in positions.values():
            all_pts.extend([Point(r.left, r.top), Point(r.right, r.bottom)])
        for route in routes:
            all_pts.extend(route.points)
            if route.label_pos:
                all_pts.append(route.label_pos)

        if all_pts:
            min_x = min(p.x for p in all_pts)
            min_y = min(p.y for p in all_pts)
            max_x = max(p.x for p in all_pts)
            max_y = max(p.y for p in all_pts)
            pad = spec.layout.padding
            canvas_rect = Rect(
                x=round(min_x - pad, 1),
                y=round(min_y - pad, 1),
                width=round((max_x - min_x) + 2 * pad, 1),
                height=round((max_y - min_y) + 2 * pad, 1),
            )
        else:
            canvas_rect = Rect(0.0, 0.0, 100.0, 100.0)

        stats = {
            "node_count": len(node_map),
            "edge_count": len(routes),
            "canvas_width": canvas_rect.width,
            "canvas_height": canvas_rect.height,
            "overlaps": overlaps,
            "algorithm": algorithm,
            "direction": spec.layout.direction,
        }

        return LaidOutDiagram(
            nodes=node_map,
            edges=routes,
            canvas_rect=canvas_rect,
            stats=stats,
        )
