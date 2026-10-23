"""Tool handler implementations for Sketchwright MCP server."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from sketchwright.config import default_settings
from sketchwright.engine.generator import DiagramGenerator
from sketchwright.errors import MCPToolError, ValidationError
from sketchwright.excalidraw.export import export_svg, write_excalidraw_file, write_svg_file
from sketchwright.excalidraw.validator import validate_excalidraw_scene
from sketchwright.layout.engine import LayoutEngine
from sketchwright.models.validation import validate_raw_input
from sketchwright.parser.text import parse_text_dsl


def handle_get_capabilities() -> dict[str, Any]:
    """Return machine-readable manifest of active runtime capabilities."""
    limits = default_settings.limits
    return {
        "product": "Sketchwright",
        "version": "0.1.0",
        "schema_versions": ["1.0"],
        "supported_shapes": [
            "rectangle",
            "rounded_rectangle",
            "ellipse",
            "diamond",
            "cylinder",
            "text",
        ],
        "supported_algorithms": ["layered", "grid", "tree"],
        "supported_directions": ["LR", "RL", "TB", "BT"],
        "supported_formats": ["excalidraw", "svg"],
        "supported_curve_styles": ["orthogonal", "straight"],
        "limits": {
            "max_input_bytes": limits.max_input_bytes,
            "max_nodes": limits.max_nodes,
            "max_edges": limits.max_edges,
            "max_label_length": limits.max_label_length,
        },
    }


def handle_create_diagram(
    specification: Optional[dict[str, Any]] = None,
    text_dsl: Optional[str] = None,
    layout_overrides: Optional[dict[str, Any]] = None,
    output_path: Optional[str] = None,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Generate an Excalidraw-compatible diagram scene from specification or text DSL."""
    if specification is None and text_dsl is None:
        raise MCPToolError("Must provide either 'specification' (JSON object) or 'text_dsl' (string).")

    try:
        if specification is not None:
            spec_data = dict(specification)
            if layout_overrides:
                curr_layout = spec_data.get("layout", {})
                curr_layout.update(layout_overrides)
                spec_data["layout"] = curr_layout
            val_res, spec = validate_raw_input(spec_data)
            if not val_res.is_valid or spec is None:
                raise ValidationError(f"Invalid specification: {'; '.join(val_res.errors)}")
        else:
            assert text_dsl is not None
            spec = parse_text_dsl(text_dsl)
            if layout_overrides:
                if "algorithm" in layout_overrides:
                    spec.layout.algorithm = layout_overrides["algorithm"]
                if "direction" in layout_overrides:
                    spec.layout.direction = layout_overrides["direction"]

        # Run generator pipeline
        generator = DiagramGenerator(spec)
        result = generator.generate()

        written_path: Optional[str] = None
        if output_path:
            p = Path(output_path)
            if p.suffix.lower() == ".svg":
                target = write_svg_file(result.scene, p, overwrite=overwrite, enforce_boundary=True)
            else:
                target = write_excalidraw_file(result.scene, p, overwrite=overwrite, enforce_boundary=True)
            written_path = str(target)

        return {
            "scene": result.scene,
            "summary": result.to_summary(),
            "output_file": written_path,
            "validation": result.validation.to_dict(),
            "warnings": result.warnings,
        }
    except Exception as e:
        raise MCPToolError(f"Diagram generation failed: {e}") from e


def handle_validate_diagram(
    specification: Optional[dict[str, Any]] = None,
    scene: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Validate a diagram specification or an Excalidraw scene JSON."""
    if specification is None and scene is None:
        raise MCPToolError("Must provide either 'specification' or 'scene' to validate.")

    results: dict[str, Any] = {}
    if specification is not None:
        val_res, _ = validate_raw_input(specification)
        results["specification_validation"] = val_res.to_dict()

    if scene is not None:
        scene_res = validate_excalidraw_scene(scene)
        results["scene_validation"] = scene_res.to_dict()

    # Determine overall validity
    is_valid = True
    if "specification_validation" in results and not results["specification_validation"]["is_valid"]:
        is_valid = False
    if "scene_validation" in results and not results["scene_validation"]["is_valid"]:
        is_valid = False

    results["is_valid"] = is_valid
    return results


def handle_layout_diagram(
    specification: dict[str, Any],
    algorithm: Optional[str] = None,
    direction: Optional[str] = None,
) -> dict[str, Any]:
    """Calculate deterministic geometry positions and routes without full scene serialization."""
    try:
        spec_data = dict(specification)
        if algorithm or direction:
            curr_layout = spec_data.get("layout", {})
            if algorithm:
                curr_layout["algorithm"] = algorithm
            if direction:
                curr_layout["direction"] = direction
            spec_data["layout"] = curr_layout

        val_res, spec = validate_raw_input(spec_data)
        if not val_res.is_valid or spec is None:
            raise ValidationError(f"Invalid specification: {'; '.join(val_res.errors)}")

        engine = LayoutEngine(spec)
        laid_out = engine.layout()

        node_positions = {
            nid: {
                "x": n.rect.x,
                "y": n.rect.y,
                "width": n.rect.width,
                "height": n.rect.height,
                "shape": n.shape,
            }
            for nid, n in laid_out.nodes.items()
        }

        routes = [
            {
                "edge_id": r.edge_id,
                "source": r.source_id,
                "target": r.target_id,
                "points": [{"x": p.x, "y": p.y} for p in r.points],
                "label": r.label,
                "label_pos": {"x": r.label_pos.x, "y": r.label_pos.y} if r.label_pos else None,
                "is_self_loop": r.is_self_loop,
            }
            for r in laid_out.edges
        ]

        canvas = {
            "x": laid_out.canvas_rect.x,
            "y": laid_out.canvas_rect.y,
            "width": laid_out.canvas_rect.width,
            "height": laid_out.canvas_rect.height,
        }

        return {
            "node_positions": node_positions,
            "routes": routes,
            "canvas": canvas,
            "stats": laid_out.stats,
        }
    except Exception as e:
        raise MCPToolError(f"Layout computation failed: {e}") from e


def handle_export_diagram(
    specification: Optional[dict[str, Any]] = None,
    scene: Optional[dict[str, Any]] = None,
    format: str = "excalidraw",
    output_path: Optional[str] = None,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Export diagram to Excalidraw JSON or SVG format."""
    fmt = format.lower().strip()
    if fmt not in ("excalidraw", "svg"):
        raise MCPToolError(f"Unsupported export format '{format}'. Supported formats: 'excalidraw', 'svg'.")

    try:
        active_scene = scene
        if active_scene is None:
            if specification is None:
                raise MCPToolError("Must supply either 'scene' or 'specification' to export.")
            val_res, spec = validate_raw_input(specification)
            if not val_res.is_valid or spec is None:
                raise ValidationError(f"Invalid specification: {'; '.join(val_res.errors)}")
            generator = DiagramGenerator(spec)
            active_scene = generator.generate().scene

        written_path: Optional[str] = None
        content_preview: str

        if fmt == "svg":
            svg_content = export_svg(active_scene)
            if output_path:
                target = write_svg_file(active_scene, output_path, overwrite=overwrite, enforce_boundary=True)
                written_path = str(target)
            content_preview = svg_content[:500]
        else:
            if output_path:
                target = write_excalidraw_file(active_scene, output_path, overwrite=overwrite, enforce_boundary=True)
                written_path = str(target)
            content_preview = json.dumps(active_scene, indent=2)[:500]

        return {
            "format": fmt,
            "output_file": written_path,
            "content_preview": content_preview,
            "elements_count": len(active_scene.get("elements", [])),
            "status": "success",
        }
    except Exception as e:
        raise MCPToolError(f"Export failed: {e}") from e


def handle_update_diagram(
    specification: dict[str, Any],
    patch: dict[str, Any],
    generate_scene: bool = True,
    output_path: Optional[str] = None,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Incrementally update an existing diagram specification and optionally regenerate its scene."""
    try:
        val_res, base_spec = validate_raw_input(specification)
        if not val_res.is_valid or base_spec is None:
            raise ValidationError(f"Invalid base specification: {'; '.join(val_res.errors)}")

        from sketchwright.engine.updater import update_diagram_spec

        updated_spec = update_diagram_spec(base_spec, patch)

        response: dict[str, Any] = {
            "updated_specification": updated_spec.model_dump(exclude_none=True),
            "status": "success",
        }

        if generate_scene:
            generator = DiagramGenerator(updated_spec)
            gen_res = generator.generate()
            response["scene"] = gen_res.scene
            response["summary"] = gen_res.to_summary()

            if output_path:
                target = write_excalidraw_file(gen_res.scene, output_path, overwrite=overwrite, enforce_boundary=True)
                response["output_file"] = str(target)

        return response
    except Exception as e:
        raise MCPToolError(f"Diagram update failed: {e}") from e
