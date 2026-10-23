"""Sketchwright: Deterministic Excalidraw MCP diagram agent and layout engine."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional, Union

from sketchwright.engine.generator import DiagramGenerator, GenerationResult
from sketchwright.engine.updater import DiagramUpdatePatch, update_diagram_spec
from sketchwright.errors import (
    ConfigurationError,
    FileSystemError,
    LayoutError,
    MCPToolError,
    SerializationError,
    SketchwrightError,
    ValidationError,
)
from sketchwright.excalidraw.export import write_excalidraw_file, write_svg_file
from sketchwright.excalidraw.validator import validate_excalidraw_scene
from sketchwright.layout.engine import LaidOutDiagram, LayoutEngine
from sketchwright.mcp.tools import handle_get_capabilities
from sketchwright.models.diagram import DiagramOptions, DiagramSpec
from sketchwright.models.validation import validate_raw_input
from sketchwright.parser.text import parse_text_dsl

__version__ = "0.1.0"


def generate_diagram(
    specification: Union[dict[str, Any], DiagramSpec, str],
    output_path: Optional[Union[str, Path]] = None,
    overwrite: bool = False,
    format: str = "excalidraw",
) -> GenerationResult:
    """Public Python API: Generate a complete Excalidraw scene from specification or DSL."""
    if isinstance(specification, str):
        spec = parse_text_dsl(specification)
    elif isinstance(specification, dict):
        val_res, parsed = validate_raw_input(specification)
        if not val_res.is_valid or parsed is None:
            raise ValidationError(f"Invalid diagram specification: {'; '.join(val_res.errors)}")
        spec = parsed
    elif isinstance(specification, DiagramSpec):
        spec = specification
    else:
        raise ValidationError(f"Unsupported specification type: {type(specification).__name__}")

    generator = DiagramGenerator(spec)
    result = generator.generate()

    if output_path is not None:
        p = Path(output_path)
        if format.lower() == "svg" or p.suffix.lower() == ".svg":
            write_svg_file(result.scene, p, overwrite=overwrite)
        else:
            write_excalidraw_file(result.scene, p, overwrite=overwrite)

    return result


def validate_diagram(
    specification: Optional[dict[str, Any]] = None,
    scene: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Public Python API: Validate a specification or an Excalidraw scene."""
    if specification is None and scene is None:
        raise ValidationError("Must supply either 'specification' or 'scene' to validate.")

    output: dict[str, Any] = {}
    if specification is not None:
        v_res, _ = validate_raw_input(specification)
        output["specification"] = v_res.to_dict()

    if scene is not None:
        s_res = validate_excalidraw_scene(scene)
        output["scene"] = s_res.to_dict()

    is_valid = True
    if "specification" in output and not output["specification"]["is_valid"]:
        is_valid = False
    if "scene" in output and not output["scene"]["is_valid"]:
        is_valid = False

    output["is_valid"] = is_valid
    return output


def layout_diagram(
    specification: Union[dict[str, Any], DiagramSpec, str],
) -> LaidOutDiagram:
    """Public Python API: Compute deterministic coordinates and routing without serialization."""
    if isinstance(specification, str):
        spec = parse_text_dsl(specification)
    elif isinstance(specification, dict):
        val_res, parsed = validate_raw_input(specification)
        if not val_res.is_valid or parsed is None:
            raise ValidationError(f"Invalid diagram specification: {'; '.join(val_res.errors)}")
        spec = parsed
    elif isinstance(specification, DiagramSpec):
        spec = specification
    else:
        raise ValidationError(f"Unsupported specification type: {type(specification).__name__}")

    engine = LayoutEngine(spec)
    return engine.layout()


def export_diagram(
    scene: dict[str, Any],
    output_path: Union[str, Path],
    format: str = "excalidraw",
    overwrite: bool = False,
) -> Path:
    """Public Python API: Safely export an Excalidraw scene to disk (.excalidraw or .svg)."""
    p = Path(output_path)
    if format.lower() == "svg" or p.suffix.lower() == ".svg":
        return write_svg_file(scene, p, overwrite=overwrite)
    return write_excalidraw_file(scene, p, overwrite=overwrite)


def update_diagram(
    specification: Union[dict[str, Any], DiagramSpec],
    patch: Union[dict[str, Any], DiagramUpdatePatch],
    output_path: Optional[Union[str, Path]] = None,
    overwrite: bool = False,
) -> GenerationResult:
    """Public Python API: Incrementally mutate a diagram specification and regenerate scene."""
    if isinstance(specification, dict):
        val_res, parsed = validate_raw_input(specification)
        if not val_res.is_valid or parsed is None:
            raise ValidationError(f"Invalid diagram specification: {'; '.join(val_res.errors)}")
        spec = parsed
    elif isinstance(specification, DiagramSpec):
        spec = specification
    else:
        raise ValidationError(f"Unsupported specification type: {type(specification).__name__}")

    updated_spec = update_diagram_spec(spec, patch)
    return generate_diagram(updated_spec, output_path=output_path, overwrite=overwrite)


def get_capabilities() -> dict[str, Any]:
    """Public Python API: Return active runtime capabilities manifest."""
    return handle_get_capabilities()


__all__ = [
    "ConfigurationError",
    "DiagramOptions",
    "DiagramSpec",
    "DiagramUpdatePatch",
    "FileSystemError",
    "GenerationResult",
    "LaidOutDiagram",
    "LayoutError",
    "MCPToolError",
    "SerializationError",
    "SketchwrightError",
    "ValidationError",
    "__version__",
    "export_diagram",
    "generate_diagram",
    "get_capabilities",
    "layout_diagram",
    "update_diagram",
    "validate_diagram",
]
