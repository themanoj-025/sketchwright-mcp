"""Serialization of laid-out diagrams into official Excalidraw scene JSON."""

from __future__ import annotations

from typing import Any, Optional

from sketchwright.excalidraw.bindings import (
    create_binding,
    generate_stable_id,
    register_bound_element,
)
from sketchwright.layout.engine import LaidOutDiagram
from sketchwright.models.diagram import DiagramSpec
from sketchwright.models.elements import EdgeKind, ShapeType, StyleConfig

_PALETTES = {
    "light": {
        "canvas_bg": "#ffffff",
        "stroke": "#1e1e1e",
        "text": "#1e1e1e",
        "arrow": "#495057",
        "rectangle_bg": "#e7f5ff",
        "rounded_rectangle_bg": "#f3f0ff",
        "ellipse_bg": "#fff9db",
        "diamond_bg": "#fff4e6",
        "cylinder_bg": "#e6fcf5",
        "text_bg": "transparent",
    },
    "dark": {
        "canvas_bg": "#121212",
        "stroke": "#e0e0e0",
        "text": "#f8fafc",
        "arrow": "#94a3b8",
        "rectangle_bg": "#1e293b",
        "rounded_rectangle_bg": "#2e1065",
        "ellipse_bg": "#362b00",
        "diamond_bg": "#431407",
        "cylinder_bg": "#064e3b",
        "text_bg": "transparent",
    },
}


class ExcalidrawSerializer:
    """Serializes a laid-out diagram into a valid, deterministic Excalidraw scene."""

    def __init__(self, spec: DiagramSpec, laid_out: LaidOutDiagram) -> None:
        self.spec = spec
        self.laid_out = laid_out
        self.palette = _PALETTES["dark" if spec.style.theme == "dark" else "light"]

    def serialize(self) -> dict[str, Any]:
        """Convert diagram to full Excalidraw scene document."""
        elements: list[dict[str, Any]] = []
        node_elem_map: dict[str, str] = {}
        elem_by_id: dict[str, dict[str, Any]] = {}

        salt = self.spec.title or "diagram"

        # 1. Generate node shapes and bound text elements
        for node_id, laid_node in sorted(self.laid_out.nodes.items()):
            shape_elem_id = generate_stable_id("shape", node_id, salt=salt)
            text_elem_id = generate_stable_id("text", node_id, salt=salt)
            node_elem_map[node_id] = shape_elem_id

            shape_elem = self._create_shape_element(
                elem_id=shape_elem_id,
                node_id=node_id,
                shape=laid_node.shape,
                rect=laid_node.rect,
                style=self.spec.style,
            )
            elements.append(shape_elem)
            elem_by_id[shape_elem_id] = shape_elem

            # Bound text label inside container
            text_elem = self._create_bound_text_element(
                elem_id=text_elem_id,
                container_id=shape_elem_id,
                text=laid_node.label,
                container_rect=laid_node.rect,
                style=self.spec.style,
            )
            elements.append(text_elem)
            elem_by_id[text_elem_id] = text_elem

            # Reciprocal binding: shape container references text
            register_bound_element(shape_elem, text_elem_id, "text")

        # 2. Generate arrows and edge labels
        edge_spec_map = {e.id: e for e in self.spec.edges}
        for route in self.laid_out.edges:
            edge_id = route.edge_id
            arrow_elem_id = generate_stable_id("arrow", edge_id, salt=salt)

            src_shape_id = node_elem_map.get(route.source_id)
            tgt_shape_id = node_elem_map.get(route.target_id)

            edge_spec = edge_spec_map.get(edge_id)
            kind: EdgeKind = edge_spec.kind if edge_spec else "directed"

            arrow_elem = self._create_arrow_element(
                elem_id=arrow_elem_id,
                edge_id=edge_id,
                route_points=route.points,
                src_elem_id=src_shape_id,
                tgt_elem_id=tgt_shape_id,
                kind=kind,
                style=self.spec.style,
            )
            elements.append(arrow_elem)
            elem_by_id[arrow_elem_id] = arrow_elem

            # Reciprocal arrow bindings
            if src_shape_id and src_shape_id in elem_by_id:
                register_bound_element(elem_by_id[src_shape_id], arrow_elem_id, "arrow")
            if tgt_shape_id and tgt_shape_id in elem_by_id:
                register_bound_element(elem_by_id[tgt_shape_id], arrow_elem_id, "arrow")

            # Optional edge label
            if route.label and route.label_pos:
                edge_text_id = generate_stable_id("edge_text", edge_id, salt=salt)
                edge_text_elem = self._create_edge_text_element(
                    elem_id=edge_text_id,
                    text=route.label,
                    pos=route.label_pos,
                    style=self.spec.style,
                )
                elements.append(edge_text_elem)
                elem_by_id[edge_text_id] = edge_text_elem

        # 3. Optional diagram title
        if self.spec.title:
            title_id = generate_stable_id("title", self.spec.title, salt=salt)
            title_elem = self._create_title_element(
                elem_id=title_id,
                title=self.spec.title,
                canvas_rect=self.laid_out.canvas_rect,
                style=self.spec.style,
            )
            elements.insert(0, title_elem)

        scene = {
            "type": "excalidraw",
            "version": 2,
            "source": "https://sketchwright.dev",
            "elements": elements,
            "appState": {
                "viewBackgroundColor": self.palette["canvas_bg"],
                "gridSize": None,
            },
            "files": {},
        }

        return scene

    def _create_shape_element(
        self,
        elem_id: str,
        node_id: str,
        shape: ShapeType,
        rect: Any,
        style: StyleConfig,
    ) -> dict[str, Any]:
        """Construct an Excalidraw shape element."""
        # Map shape type to Excalidraw element type
        excal_type = "rectangle"
        roundness: Optional[dict[str, Any]] = None

        if shape == "rounded_rectangle":
            excal_type = "rectangle"
            roundness = {"type": 3}
        elif shape == "cylinder":
            # Excalidraw represents cylindrical storage via rounded container with database styling
            excal_type = "rectangle"
            roundness = {"type": 3}
        elif shape == "ellipse":
            excal_type = "ellipse"
        elif shape == "diamond":
            excal_type = "diamond"
        elif shape == "text":
            excal_type = "rectangle"
            roundness = None

        stroke_color = style.stroke_color or self.palette["stroke"]
        bg_color = style.background_color or self.palette.get(f"{shape}_bg", self.palette["rectangle_bg"])

        seed = int(elem_id[:8], 16) % 1_000_000_000
        nonce = int(elem_id[8:16], 16) % 1_000_000_000

        return {
            "id": elem_id,
            "type": excal_type,
            "x": rect.x,
            "y": rect.y,
            "width": rect.width,
            "height": rect.height,
            "angle": 0,
            "strokeColor": stroke_color,
            "backgroundColor": bg_color,
            "fillStyle": "solid",
            "strokeWidth": style.stroke_width,
            "strokeStyle": "solid",
            "roughness": style.roughness,
            "opacity": 100,
            "groupIds": [],
            "frameId": None,
            "roundness": roundness,
            "seed": seed,
            "version": 1,
            "versionNonce": nonce,
            "isDeleted": False,
            "boundElements": [],
            "updated": 1,
            "link": None,
            "locked": False,
            "customData": {"nodeId": node_id, "shape": shape},
        }

    def _create_bound_text_element(
        self,
        elem_id: str,
        container_id: str,
        text: str,
        container_rect: Any,
        style: StyleConfig,
    ) -> dict[str, Any]:
        """Construct an Excalidraw text element bound inside a container shape."""
        seed = int(elem_id[:8], 16) % 1_000_000_000
        nonce = int(elem_id[8:16], 16) % 1_000_000_000
        text_color = style.stroke_color or self.palette["text"]

        return {
            "id": elem_id,
            "type": "text",
            "x": round(container_rect.x + 8.0, 1),
            "y": round(container_rect.y + 8.0, 1),
            "width": round(max(10.0, container_rect.width - 16.0), 1),
            "height": round(max(10.0, container_rect.height - 16.0), 1),
            "angle": 0,
            "strokeColor": text_color,
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": 1,
            "strokeStyle": "solid",
            "roughness": 0,
            "opacity": 100,
            "groupIds": [],
            "frameId": None,
            "roundness": None,
            "seed": seed,
            "version": 1,
            "versionNonce": nonce,
            "isDeleted": False,
            "boundElements": None,
            "updated": 1,
            "link": None,
            "locked": False,
            "text": text,
            "fontSize": style.font_size,
            "fontFamily": 1,  # Virgil
            "textAlign": "center",
            "verticalAlign": "middle",
            "baseline": round(style.font_size * 0.8, 1),
            "containerId": container_id,
            "originalText": text,
            "lineHeight": 1.25,
        }

    def _create_arrow_element(
        self,
        elem_id: str,
        edge_id: str,
        route_points: list[Any],
        src_elem_id: Optional[str],
        tgt_elem_id: Optional[str],
        kind: EdgeKind,
        style: StyleConfig,
    ) -> dict[str, Any]:
        """Construct an Excalidraw arrow element with bindings and relative points."""
        start_pt = route_points[0]
        rel_points = [[0.0, 0.0]]
        for pt in route_points[1:]:
            rel_points.append([round(pt.x - start_pt.x, 1), round(pt.y - start_pt.y, 1)])

        xs = [p[0] for p in rel_points]
        ys = [p[1] for p in rel_points]
        w = round(max(abs(max(xs) - min(xs)), 1.0), 1)
        h = round(max(abs(max(ys) - min(ys)), 1.0), 1)

        seed = int(elem_id[:8], 16) % 1_000_000_000
        nonce = int(elem_id[8:16], 16) % 1_000_000_000
        stroke_color = self.palette["arrow"]

        start_binding = create_binding(src_elem_id) if src_elem_id else None
        end_binding = create_binding(tgt_elem_id) if tgt_elem_id else None

        start_arrowhead = "arrow" if kind == "bidirectional" else None
        end_arrowhead = "arrow" if kind in ("directed", "bidirectional") else None

        return {
            "id": elem_id,
            "type": "arrow",
            "x": start_pt.x,
            "y": start_pt.y,
            "width": w,
            "height": h,
            "angle": 0,
            "strokeColor": stroke_color,
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": style.stroke_width,
            "strokeStyle": "solid",
            "roughness": style.roughness,
            "opacity": 100,
            "groupIds": [],
            "frameId": None,
            "roundness": {"type": 2},
            "seed": seed,
            "version": 1,
            "versionNonce": nonce,
            "isDeleted": False,
            "boundElements": None,
            "updated": 1,
            "link": None,
            "locked": False,
            "points": rel_points,
            "lastCommittedPoint": None,
            "startBinding": start_binding,
            "endBinding": end_binding,
            "startArrowhead": start_arrowhead,
            "endArrowhead": end_arrowhead,
            "elbowed": True,
            "customData": {"edgeId": edge_id, "kind": kind},
        }

    def _create_edge_text_element(
        self,
        elem_id: str,
        text: str,
        pos: Any,
        style: StyleConfig,
    ) -> dict[str, Any]:
        """Construct an Excalidraw text label placed alongside an edge."""
        seed = int(elem_id[:8], 16) % 1_000_000_000
        nonce = int(elem_id[8:16], 16) % 1_000_000_000
        text_color = self.palette["arrow"]
        font_size = max(12, style.font_size - 2)

        w = round(len(text) * font_size * 0.6 + 10.0, 1)
        h = round(font_size * 1.3 + 4.0, 1)

        return {
            "id": elem_id,
            "type": "text",
            "x": round(pos.x - w / 2.0, 1),
            "y": round(pos.y, 1),
            "width": w,
            "height": h,
            "angle": 0,
            "strokeColor": text_color,
            "backgroundColor": self.palette["canvas_bg"],
            "fillStyle": "solid",
            "strokeWidth": 1,
            "strokeStyle": "solid",
            "roughness": 0,
            "opacity": 100,
            "groupIds": [],
            "frameId": None,
            "roundness": None,
            "seed": seed,
            "version": 1,
            "versionNonce": nonce,
            "isDeleted": False,
            "boundElements": None,
            "updated": 1,
            "link": None,
            "locked": False,
            "text": text,
            "fontSize": font_size,
            "fontFamily": 1,
            "textAlign": "center",
            "verticalAlign": "middle",
            "baseline": round(font_size * 0.8, 1),
            "containerId": None,
            "originalText": text,
            "lineHeight": 1.25,
        }

    def _create_title_element(
        self,
        elem_id: str,
        title: str,
        canvas_rect: Any,
        style: StyleConfig,
    ) -> dict[str, Any]:
        """Construct a prominent title heading above the diagram."""
        seed = int(elem_id[:8], 16) % 1_000_000_000
        nonce = int(elem_id[8:16], 16) % 1_000_000_000
        font_size = style.font_size + 8
        w = round(len(title) * font_size * 0.65 + 20.0, 1)
        h = round(font_size * 1.4, 1)

        return {
            "id": elem_id,
            "type": "text",
            "x": round(canvas_rect.left + 20.0, 1),
            "y": round(canvas_rect.top - h - 10.0, 1),
            "width": w,
            "height": h,
            "angle": 0,
            "strokeColor": self.palette["stroke"],
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": 2,
            "strokeStyle": "solid",
            "roughness": 0,
            "opacity": 100,
            "groupIds": [],
            "frameId": None,
            "roundness": None,
            "seed": seed,
            "version": 1,
            "versionNonce": nonce,
            "isDeleted": False,
            "boundElements": None,
            "updated": 1,
            "link": None,
            "locked": False,
            "text": title,
            "fontSize": font_size,
            "fontFamily": 2,  # Helvetica for clean titles
            "textAlign": "left",
            "verticalAlign": "top",
            "baseline": round(font_size * 0.8, 1),
            "containerId": None,
            "originalText": title,
            "lineHeight": 1.25,
        }
