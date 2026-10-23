"""Validator for generated or imported Excalidraw scenes."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SceneValidationResult:
    """Report detailing the structural and geometric validity of an Excalidraw scene."""

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


def validate_excalidraw_scene(scene: dict[str, Any]) -> SceneValidationResult:
    """Validate that an Excalidraw scene conforms to the Excalidraw v2 specification."""
    errors: list[str] = []
    warnings: list[str] = []

    # 1. Top level document validation
    if not isinstance(scene, dict):
        return SceneValidationResult(
            is_valid=False,
            errors=[f"Excalidraw scene root must be a JSON object, got {type(scene).__name__}"],
        )

    if scene.get("type") != "excalidraw":
        errors.append(f"Invalid scene type '{scene.get('type')}'. Expected 'excalidraw'.")

    version = scene.get("version")
    if version != 2:
        warnings.append(f"Scene version is {version}; expected version 2.")

    elements = scene.get("elements")
    if not isinstance(elements, list):
        errors.append(f"Scene 'elements' must be a list, got {type(elements).__name__}.")
        return SceneValidationResult(is_valid=False, errors=errors, warnings=warnings)

    if not isinstance(scene.get("appState"), dict):
        warnings.append("Scene 'appState' is missing or not an object.")

    if not isinstance(scene.get("files"), dict):
        warnings.append("Scene 'files' is missing or not an object.")

    # 2. Element validation
    element_ids: set[str] = set()
    element_map: dict[str, dict[str, Any]] = {}
    valid_types = {"rectangle", "ellipse", "diamond", "text", "arrow", "line"}

    for idx, elem in enumerate(elements):
        if not isinstance(elem, dict):
            errors.append(f"Element at index {idx} is not an object.")
            continue

        elem_id = elem.get("id")
        if not elem_id or not isinstance(elem_id, str):
            errors.append(f"Element at index {idx} has invalid or missing 'id'.")
            continue

        if elem_id in element_ids:
            errors.append(f"Duplicate element id '{elem_id}' at index {idx}.")
        element_ids.add(elem_id)
        element_map[elem_id] = elem

        elem_type = elem.get("type")
        if elem_type not in valid_types:
            errors.append(f"Element '{elem_id}' has unsupported type '{elem_type}'.")

        # Numeric bounds
        for num_field in ("x", "y", "width", "height"):
            val = elem.get(num_field)
            if val is None or not isinstance(val, (int, float)) or not math.isfinite(val):
                errors.append(f"Element '{elem_id}' has invalid numeric {num_field}: {val}")

        w = elem.get("width", 0)
        h = elem.get("height", 0)
        if isinstance(w, (int, float)) and w < 0:
            errors.append(f"Element '{elem_id}' has negative width: {w}")
        if isinstance(h, (int, float)) and h < 0:
            errors.append(f"Element '{elem_id}' has negative height: {h}")

    # 3. Binding integrity and reciprocal checks
    for elem_id, elem in element_map.items():
        elem_type = elem.get("type")

        # Arrow bindings
        if elem_type == "arrow":
            start_b = elem.get("startBinding")
            if isinstance(start_b, dict):
                src_id = start_b.get("elementId")
                if not src_id or src_id not in element_map:
                    errors.append(f"Arrow '{elem_id}' has dangling startBinding referencing '{src_id}'.")
                else:
                    target_elem = element_map[src_id]
                    bound = target_elem.get("boundElements") or []
                    bound_ids = {b.get("id") for b in bound if isinstance(b, dict)}
                    if elem_id not in bound_ids:
                        warnings.append(
                            f"Target '{src_id}' is missing reciprocal boundElements entry for arrow '{elem_id}'."
                        )

            end_b = elem.get("endBinding")
            if isinstance(end_b, dict):
                tgt_id = end_b.get("elementId")
                if not tgt_id or tgt_id not in element_map:
                    errors.append(f"Arrow '{elem_id}' has dangling endBinding referencing '{tgt_id}'.")
                else:
                    target_elem = element_map[tgt_id]
                    bound = target_elem.get("boundElements") or []
                    bound_ids = {b.get("id") for b in bound if isinstance(b, dict)}
                    if elem_id not in bound_ids:
                        warnings.append(
                            f"Target '{tgt_id}' is missing reciprocal boundElements entry for arrow '{elem_id}'."
                        )

        # Text container binding
        if elem_type == "text":
            container_id = elem.get("containerId")
            if container_id:
                if container_id not in element_map:
                    errors.append(f"Text '{elem_id}' references missing containerId '{container_id}'.")
                else:
                    container = element_map[container_id]
                    bound = container.get("boundElements") or []
                    bound_ids = {b.get("id") for b in bound if isinstance(b, dict)}
                    if elem_id not in bound_ids:
                        warnings.append(
                            f"Container '{container_id}' is missing reciprocal boundElements entry for text '{elem_id}'."
                        )

    stats = {
        "total_elements": len(elements),
        "shapes": sum(
            1 for e in elements if isinstance(e, dict) and e.get("type") in ("rectangle", "ellipse", "diamond")
        ),
        "arrows": sum(1 for e in elements if isinstance(e, dict) and e.get("type") == "arrow"),
        "texts": sum(1 for e in elements if isinstance(e, dict) and e.get("type") == "text"),
    }

    return SceneValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        stats=stats,
    )
