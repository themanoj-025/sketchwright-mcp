"""Comprehensive semantic and structural validation for diagram specifications."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from pydantic import ValidationError as PydanticValidationError

from sketchwright.config import Limits, default_settings
from sketchwright.models.diagram import DiagramSpec


@dataclass
class ValidationResult:
    """Detailed validation diagnostic report."""

    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    stats: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "stats": self.stats,
        }


def validate_diagram_spec(
    spec: DiagramSpec,
    limits: Optional[Limits] = None,
) -> ValidationResult:
    """Perform deep semantic validation of a DiagramSpec against domain rules and limits."""
    active_limits = limits or default_settings.limits
    errors: list[str] = []
    warnings: list[str] = []

    # 1. Resource limits
    node_count = len(spec.nodes)
    edge_count = len(spec.edges)
    group_count = len(spec.groups)

    if node_count > active_limits.max_nodes:
        errors.append(f"Node count {node_count} exceeds maximum permitted limit ({active_limits.max_nodes}).")
    if edge_count > active_limits.max_edges:
        errors.append(f"Edge count {edge_count} exceeds maximum permitted limit ({active_limits.max_edges}).")

    # 2. Node uniqueness and constraints
    node_ids: set[str] = set()
    duplicate_nodes: set[str] = set()

    for node in spec.nodes:
        if node.id in node_ids:
            duplicate_nodes.add(node.id)
        else:
            node_ids.add(node.id)

        if len(node.label) > active_limits.max_label_length:
            errors.append(f"Label for node '{node.id}' exceeds maximum length ({active_limits.max_label_length}).")

    if duplicate_nodes:
        errors.append(f"Duplicate node IDs detected: {sorted(duplicate_nodes)}")

    # 3. Group references
    group_ids: set[str] = {g.id for g in spec.groups}
    for node in spec.nodes:
        if node.group and node.group not in group_ids:
            warnings.append(f"Node '{node.id}' references group '{node.group}' which is not declared in groups.")

    # 4. Edge uniqueness and valid endpoint references
    edge_ids: set[str] = set()
    duplicate_edges: set[str] = set()

    for edge in spec.edges:
        if edge.id in edge_ids:
            duplicate_edges.add(edge.id)
        else:
            edge_ids.add(edge.id)

        if edge.source not in node_ids:
            errors.append(f"Edge '{edge.id}' has unresolved source endpoint '{edge.source}'.")
        if edge.target not in node_ids:
            errors.append(f"Edge '{edge.id}' has unresolved target endpoint '{edge.target}'.")

        if edge.source == edge.target:
            warnings.append(f"Edge '{edge.id}' is a self-loop (source and target are '{edge.source}').")

    if duplicate_edges:
        errors.append(f"Duplicate edge IDs detected: {sorted(duplicate_edges)}")

    stats = {
        "nodes": node_count,
        "edges": edge_count,
        "groups": group_count,
        "algorithm": spec.layout.algorithm,
        "direction": spec.layout.direction,
    }

    is_valid = len(errors) == 0
    return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings, stats=stats)


def validate_raw_input(
    data: dict[str, Any],
    limits: Optional[Limits] = None,
) -> tuple[ValidationResult, Optional[DiagramSpec]]:
    """Parse raw dictionary data and validate according to canonical schema."""
    try:
        spec = DiagramSpec.model_validate(data)
    except PydanticValidationError as e:
        errors: list[str] = []
        for err in e.errors():
            loc = " -> ".join(str(p) for p in err["loc"])
            msg = err["msg"]
            errors.append(f"Field '{loc}': {msg}")
        return ValidationResult(is_valid=False, errors=errors, warnings=[]), None
    except Exception as e:
        return ValidationResult(is_valid=False, errors=[str(e)], warnings=[]), None

    result = validate_diagram_spec(spec, limits=limits)
    return result, (spec if result.is_valid else None)
