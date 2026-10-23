"""End-to-end diagram generation pipeline connecting layout, serialization, and validation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from sketchwright.errors import ValidationError
from sketchwright.excalidraw.serializer import ExcalidrawSerializer
from sketchwright.excalidraw.validator import SceneValidationResult, validate_excalidraw_scene
from sketchwright.layout.engine import LaidOutDiagram, LayoutEngine
from sketchwright.models.diagram import DiagramSpec
from sketchwright.models.validation import validate_diagram_spec


@dataclass
class GenerationResult:
    """The complete result of generating an Excalidraw diagram."""

    scene: dict[str, Any]
    validation: SceneValidationResult
    laid_out: LaidOutDiagram
    stats: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def to_summary(self) -> dict[str, Any]:
        """Produce a concise, machine-readable summary suitable for MCP tool responses."""
        return {
            "title": self.laid_out.stats.get("title"),
            "valid": self.validation.is_valid,
            "element_count": len(self.scene.get("elements", [])),
            "nodes_count": len(self.laid_out.nodes),
            "edges_count": len(self.laid_out.edges),
            "canvas_dimensions": {
                "width": self.laid_out.canvas_rect.width,
                "height": self.laid_out.canvas_rect.height,
            },
            "warnings": self.warnings + self.validation.warnings,
        }


class DiagramGenerator:
    """High-level generator executing validation, layout, serialization, and scene verification."""

    def __init__(self, spec: DiagramSpec) -> None:
        self.spec = spec

    def generate(self) -> GenerationResult:
        """Run the complete deterministic generation pipeline."""
        # 1. Spec semantic validation
        spec_val = validate_diagram_spec(self.spec)
        if not spec_val.is_valid:
            raise ValidationError(
                f"Diagram specification is invalid: {'; '.join(spec_val.errors)}",
                details={"errors": spec_val.errors, "warnings": spec_val.warnings},
            )

        # 2. Layout execution
        layout_engine = LayoutEngine(self.spec)
        laid_out = layout_engine.layout()

        # 3. Excalidraw serialization
        serializer = ExcalidrawSerializer(self.spec, laid_out)
        scene = serializer.serialize()

        # 4. Scene validation
        scene_val = validate_excalidraw_scene(scene)

        # Aggregate warnings
        all_warnings: list[str] = list(spec_val.warnings)
        if laid_out.stats.get("overlaps"):
            overlap_pairs = [f"{u}<->{v}" for u, v in laid_out.stats["overlaps"]]
            all_warnings.append(f"Visual overlap detected between nodes: {', '.join(overlap_pairs)}")

        all_warnings.extend(scene_val.warnings)

        stats = {
            "algorithm": self.spec.layout.algorithm,
            "direction": self.spec.layout.direction,
            "nodes": len(laid_out.nodes),
            "edges": len(laid_out.edges),
            "canvas_width": laid_out.canvas_rect.width,
            "canvas_height": laid_out.canvas_rect.height,
        }

        return GenerationResult(
            scene=scene,
            validation=scene_val,
            laid_out=laid_out,
            stats=stats,
            warnings=all_warnings,
        )
