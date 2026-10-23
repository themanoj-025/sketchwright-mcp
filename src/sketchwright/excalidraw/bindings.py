"""Arrow bindings and container binding management for Excalidraw scenes."""

from __future__ import annotations

import hashlib
from typing import Any


def generate_stable_id(prefix: str, identifier: str, salt: str = "sketchwright") -> str:
    """Generate a deterministic, 16-character hexadecimal ID for Excalidraw elements.

    Guarantees cross-run determinism without depending on Python's randomized hash().
    """
    raw = f"{salt}:{prefix}:{identifier}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def create_binding(element_id: str, focus: float = 0.0, gap: float = 4.0) -> dict[str, Any]:
    """Create a startBinding or endBinding record."""
    return {
        "elementId": element_id,
        "focus": focus,
        "gap": gap,
    }


def register_bound_element(
    target_element: dict[str, Any],
    bound_id: str,
    bound_type: str,  # "text" | "arrow"
) -> None:
    """Register reciprocal binding in the target element's boundElements array."""
    if "boundElements" not in target_element or target_element["boundElements"] is None:
        target_element["boundElements"] = []

    # Check for existing registration
    existing_ids = {b["id"] for b in target_element["boundElements"] if isinstance(b, dict)}
    if bound_id not in existing_ids:
        target_element["boundElements"].append(
            {
                "id": bound_id,
                "type": bound_type,
            }
        )
