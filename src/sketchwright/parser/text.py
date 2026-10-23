"""Deterministic textual DSL parser for lightweight diagram definitions."""

from __future__ import annotations

import re
from typing import Optional

from sketchwright.config import Limits, default_settings
from sketchwright.errors import ValidationError
from sketchwright.models.diagram import DiagramOptions, DiagramSpec
from sketchwright.models.elements import (
    EdgeKind,
    EdgeSpec,
    LayoutAlgorithm,
    LayoutConfig,
    LayoutDirection,
    NodeSpec,
    ShapeType,
    StyleConfig,
)
from sketchwright.models.validation import validate_diagram_spec

_NODE_DEF_REGEX = re.compile(r"^\[\s*([a-zA-Z0-9_\-\.:]+)\s*(?::\s*([a-zA-Z0-9_\-]+)\s*)?(?::\s*(.*?)\s*)?\]$")
_EDGE_DEF_REGEX = re.compile(r"^([a-zA-Z0-9_\-\.:]+)\s*(\-\->|\->|\-\-|<->)\s*([a-zA-Z0-9_\-\.:]+)(?:\s*:\s*(.*?))?$")


def parse_text_dsl(
    text: str,
    limits: Optional[Limits] = None,
) -> DiagramSpec:
    """Parse a simple, deterministic textual diagram DSL into a DiagramSpec.

    Format:
      # Comments
      title: Example Diagram
      direction: LR | TB | RL | BT
      algorithm: layered | grid

      # Nodes:
      [id: shape: label] or [id: label] or [id]
      Shapes: rectangle, rounded_rectangle, ellipse, diamond, cylinder

      # Edges:
      source -> target: Optional Label
      source <-> target: Bidirectional
      source -- target: Undirected
    """
    active_limits = limits or default_settings.limits
    raw_bytes = len(text.encode("utf-8"))
    if raw_bytes > active_limits.max_input_bytes:
        raise ValidationError(f"Input text exceeds maximum byte limit ({raw_bytes} > {active_limits.max_input_bytes}).")

    title: Optional[str] = None
    direction: LayoutDirection = "LR"
    algorithm: LayoutAlgorithm = "layered"
    theme: str = "light"

    nodes_map: dict[str, NodeSpec] = {}
    edges_list: list[EdgeSpec] = []
    edge_counter = 1

    lines = text.splitlines()
    for idx, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("//"):
            continue

        # Header directives
        lower = line.lower()
        if lower.startswith("title:"):
            title = line[6:].strip()
            continue
        if lower.startswith("direction:"):
            val = line[10:].strip().upper()
            if val in ("LR", "RL", "TB", "BT"):
                direction = val  # type: ignore[assignment]
            else:
                raise ValidationError(f"Line {idx}: Unsupported direction '{val}'. Expected LR, RL, TB, or BT.")
            continue
        if lower.startswith("algorithm:"):
            val = line[10:].strip().lower()
            if val in ("layered", "grid", "tree"):
                algorithm = val  # type: ignore[assignment]
            else:
                raise ValidationError(f"Line {idx}: Unsupported algorithm '{val}'. Expected layered, grid, or tree.")
            continue
        if lower.startswith("theme:"):
            val = line[6:].strip().lower()
            if val in ("light", "dark"):
                theme = val
            continue

        # Node definition: [id: shape: label]
        node_match = _NODE_DEF_REGEX.match(line)
        if node_match:
            node_id = node_match.group(1).strip()
            part2 = (node_match.group(2) or "").strip()
            part3 = (node_match.group(3) or "").strip()

            valid_shapes = (
                "rectangle",
                "rounded_rectangle",
                "ellipse",
                "diamond",
                "cylinder",
                "text",
            )
            if part2 and part2.lower() in valid_shapes:
                shape: ShapeType = part2.lower()  # type: ignore[assignment]
                label = part3 if part3 else node_id
            else:
                shape = "rectangle"
                label = f"{part2} {part3}".strip() if (part2 or part3) else node_id

            if node_id in nodes_map:
                raise ValidationError(f"Line {idx}: Duplicate node declaration '{node_id}'.")

            nodes_map[node_id] = NodeSpec(id=node_id, label=label, shape=shape)
            continue

        # Edge definition: source -> target: label
        edge_match = _EDGE_DEF_REGEX.match(line)
        if edge_match:
            src = edge_match.group(1).strip()
            arrow = edge_match.group(2).strip()
            tgt = edge_match.group(3).strip()
            edge_label = (edge_match.group(4) or "").strip() or None

            # Auto-declare nodes if not already declared
            if src not in nodes_map:
                nodes_map[src] = NodeSpec(id=src, label=src, shape="rectangle")
            if tgt not in nodes_map:
                nodes_map[tgt] = NodeSpec(id=tgt, label=tgt, shape="rectangle")

            kind: EdgeKind = "directed"
            if arrow == "<->":
                kind = "bidirectional"
            elif arrow == "--":
                kind = "undirected"

            edge_id = f"e{edge_counter}_{src}_{tgt}"
            edge_counter += 1
            edges_list.append(EdgeSpec(id=edge_id, source=src, target=tgt, label=edge_label, kind=kind))
            continue

        raise ValidationError(
            f"Line {idx}: Unrecognized DSL syntax '{line}'. Expected node '[id: shape: label]' or edge 'src -> tgt: label'."
        )

    spec = DiagramSpec(
        schema_version="1.0",
        title=title,
        layout=LayoutConfig(algorithm=algorithm, direction=direction),
        style=StyleConfig(theme="dark" if theme == "dark" else "light"),
        nodes=list(nodes_map.values()),
        edges=edges_list,
        options=DiagramOptions(deterministic=True),
    )

    result = validate_diagram_spec(spec, limits=active_limits)
    if not result.is_valid:
        raise ValidationError(f"DSL diagram validation failed: {'; '.join(result.errors)}")

    return spec
