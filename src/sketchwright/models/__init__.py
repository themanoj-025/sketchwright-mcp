"""Domain models and validation for Sketchwright."""

from sketchwright.models.diagram import DiagramOptions, DiagramSpec
from sketchwright.models.elements import (
    EdgeKind,
    EdgeSpec,
    GroupSpec,
    LayoutAlgorithm,
    LayoutConfig,
    LayoutDirection,
    NodeSpec,
    ShapeType,
    StyleConfig,
)
from sketchwright.models.validation import (
    ValidationResult,
    validate_diagram_spec,
    validate_raw_input,
)

__all__ = [
    "DiagramOptions",
    "DiagramSpec",
    "EdgeKind",
    "EdgeSpec",
    "GroupSpec",
    "LayoutAlgorithm",
    "LayoutConfig",
    "LayoutDirection",
    "NodeSpec",
    "ShapeType",
    "StyleConfig",
    "ValidationResult",
    "validate_diagram_spec",
    "validate_raw_input",
]
