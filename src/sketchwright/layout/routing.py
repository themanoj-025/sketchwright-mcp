"""Deterministic edge routing and label positioning."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from sketchwright.layout.geometry import Point, Rect, get_shape_boundary_anchor
from sketchwright.models.diagram import DiagramSpec
from sketchwright.models.elements import LayoutDirection


@dataclass
class EdgeRoute:
    """Calculated geometric route for an edge."""

    edge_id: str
    source_id: str
    target_id: str
    points: list[Point]
    label: Optional[str]
    label_pos: Optional[Point]
    is_self_loop: bool = False


def route_edges(
    spec: DiagramSpec,
    positions: dict[str, Rect],
) -> list[EdgeRoute]:
    """Calculate deterministic edge routes and label positions."""
    routes: list[EdgeRoute] = []
    direction: LayoutDirection = spec.layout.direction
    curve_style = spec.options.curve_style

    node_shapes = {n.id: n.shape for n in spec.nodes}

    # Parallel edge tracking for distinct offsets
    pair_counts: dict[tuple[str, str], int] = {}

    for edge in spec.edges:
        if edge.source not in positions or edge.target not in positions:
            continue

        pair_key = (min(edge.source, edge.target), max(edge.source, edge.target))
        edge_index = pair_counts.get(pair_key, 0)
        pair_counts[pair_key] = edge_index + 1

        src_rect = positions[edge.source]
        tgt_rect = positions[edge.target]
        src_shape = node_shapes.get(edge.source, "rectangle")
        tgt_shape = node_shapes.get(edge.target, "rectangle")

        # 1. Self loop routing
        if edge.source == edge.target:
            r = src_rect
            start = Point(r.center_x, r.top)
            p1 = Point(
                round(r.center_x + 25.0 + edge_index * 15.0, 1),
                round(r.top - 25.0 - edge_index * 15.0, 1),
            )
            p2 = Point(
                round(r.right + 25.0 + edge_index * 15.0, 1),
                round(r.center_y - 25.0 - edge_index * 15.0, 1),
            )
            end = Point(r.right, r.center_y)

            pts = [start, p1, p2, end]
            label_pos = Point(p1.x, round(p1.y - 12.0, 1)) if edge.label else None

            routes.append(
                EdgeRoute(
                    edge_id=edge.id,
                    source_id=edge.source,
                    target_id=edge.target,
                    points=pts,
                    label=edge.label,
                    label_pos=label_pos,
                    is_self_loop=True,
                )
            )
            continue

        # 2. Preferred contact sides
        pref_src, pref_tgt = _get_preferred_sides(direction, src_rect, tgt_rect)

        start = get_shape_boundary_anchor(src_rect, tgt_rect.center, shape=src_shape, preferred_side=pref_src)
        end = get_shape_boundary_anchor(tgt_rect, src_rect.center, shape=tgt_shape, preferred_side=pref_tgt)

        if curve_style == "straight":
            pts = [start, end]
        else:
            # Orthogonal stepped routing
            pts = _compute_orthogonal_route(direction, start, end, src_rect, tgt_rect, edge_index)

        # Label placement at segment midpoint with clearance offset
        label_pos = _calculate_label_position(pts) if edge.label else None

        routes.append(
            EdgeRoute(
                edge_id=edge.id,
                source_id=edge.source,
                target_id=edge.target,
                points=pts,
                label=edge.label,
                label_pos=label_pos,
                is_self_loop=False,
            )
        )

    return routes


def _get_preferred_sides(
    direction: LayoutDirection,
    src_rect: Rect,
    tgt_rect: Rect,
) -> tuple[Optional[str], Optional[str]]:
    """Determine best exit and entry sides based on direction and relative positions."""
    if direction == "LR":
        if tgt_rect.left >= src_rect.right:
            return "R", "L"
        return "R", "R"
    elif direction == "RL":
        if tgt_rect.right <= src_rect.left:
            return "L", "R"
        return "L", "L"
    elif direction == "TB":
        if tgt_rect.top >= src_rect.bottom:
            return "B", "T"
        return "B", "B"
    elif direction == "BT":
        if tgt_rect.bottom <= src_rect.top:
            return "T", "B"
        return "T", "T"
    return None, None


def _compute_orthogonal_route(
    direction: LayoutDirection,
    start: Point,
    end: Point,
    src_rect: Rect,
    tgt_rect: Rect,
    parallel_offset_index: int,
) -> list[Point]:
    """Compute orthogonal bend points with clearance and parallel offset handling."""
    offset = parallel_offset_index * 12.0

    if direction in ("LR", "RL"):
        # Forward progressive edge
        if (direction == "LR" and end.x >= start.x) or (direction == "RL" and end.x <= start.x):
            mid_x = round((start.x + end.x) / 2.0 + offset, 1)
            # If Y is practically identical, use single straight line
            if abs(start.y - end.y) < 2.0:
                return [start, end]
            return [start, Point(mid_x, start.y), Point(mid_x, end.y), end]
        else:
            # Backward loop edge (cycles): route around
            route_y = round(max(src_rect.bottom, tgt_rect.bottom) + 30.0 + offset, 1)
            p1 = Point(round(start.x + (20.0 if direction == "LR" else -20.0), 1), start.y)
            p2 = Point(p1.x, route_y)
            p3 = Point(round(end.x - (20.0 if direction == "LR" else -20.0), 1), route_y)
            p4 = Point(p3.x, end.y)
            return [start, p1, p2, p3, p4, end]

    else:  # TB, BT
        if (direction == "TB" and end.y >= start.y) or (direction == "BT" and end.y <= start.y):
            mid_y = round((start.y + end.y) / 2.0 + offset, 1)
            if abs(start.x - end.x) < 2.0:
                return [start, end]
            return [start, Point(start.x, mid_y), Point(end.x, mid_y), end]
        else:
            # Backward loop edge: route around
            route_x = round(max(src_rect.right, tgt_rect.right) + 30.0 + offset, 1)
            p1 = Point(start.x, round(start.y + (20.0 if direction == "TB" else -20.0), 1))
            p2 = Point(route_x, p1.y)
            p3 = Point(route_x, round(end.y - (20.0 if direction == "TB" else -20.0), 1))
            p4 = Point(end.x, p3.y)
            return [start, p1, p2, p3, p4, end]


def _calculate_label_position(points: list[Point]) -> Point:
    """Calculate the midpoint along the route points and apply a small vertical clearance offset."""
    if len(points) == 2:
        mid_x = (points[0].x + points[1].x) / 2.0
        mid_y = (points[0].y + points[1].y) / 2.0 - 12.0
        return Point(round(mid_x, 1), round(mid_y, 1))

    # For 4-point stepped paths, the middle segment [1]->[2] is the connecting span
    if len(points) == 4:
        p1, p2 = points[1], points[2]
        mid_x = (p1.x + p2.x) / 2.0 + 8.0
        mid_y = (p1.y + p2.y) / 2.0
        return Point(round(mid_x, 1), round(mid_y, 1))

    # General polyline midpoint
    mid_idx = len(points) // 2
    p = points[mid_idx]
    return Point(round(p.x, 1), round(p.y - 12.0, 1))
