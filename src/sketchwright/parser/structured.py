"""Structured JSON parsing with security controls and byte-size enforcement."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, Union

from sketchwright.config import Limits, default_settings
from sketchwright.errors import FileSystemError, ValidationError
from sketchwright.models.diagram import DiagramSpec
from sketchwright.models.validation import validate_raw_input


def parse_json_string(
    content: str,
    limits: Optional[Limits] = None,
) -> DiagramSpec:
    """Parse and validate a diagram specification from a JSON string.

    Enforces input byte size limits to prevent resource exhaustion attacks.
    """
    active_limits = limits or default_settings.limits
    raw_bytes = len(content.encode("utf-8"))

    if raw_bytes > active_limits.max_input_bytes:
        raise ValidationError(
            f"Input size ({raw_bytes} bytes) exceeds maximum limit of {active_limits.max_input_bytes} bytes.",
            details={"byte_size": raw_bytes, "max_bytes": active_limits.max_input_bytes},
        )

    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        raise ValidationError(
            f"Invalid JSON syntax at line {e.lineno}, column {e.colno}: {e.msg}",
            details={"lineno": e.lineno, "colno": e.colno, "error": e.msg},
        ) from e

    if not isinstance(data, dict):
        raise ValidationError(
            f"Diagram specification root must be a JSON object, got {type(data).__name__}.",
            details={"root_type": type(data).__name__},
        )

    result, spec = validate_raw_input(data, limits=active_limits)
    if not result.is_valid or spec is None:
        raise ValidationError(
            f"Diagram validation failed with {len(result.errors)} error(s): {'; '.join(result.errors[:5])}",
            details={"errors": result.errors, "warnings": result.warnings},
        )

    return spec


def parse_json_file(
    file_path: Union[str, Path],
    limits: Optional[Limits] = None,
) -> DiagramSpec:
    """Read, parse, and validate a diagram specification from a local file."""
    path = Path(file_path).resolve()
    if not path.is_file():
        raise FileSystemError(
            f"File does not exist or is not a regular file: {path}",
            details={"path": str(path)},
        )

    try:
        file_size = path.stat().st_size
        active_limits = limits or default_settings.limits
        if file_size > active_limits.max_input_bytes:
            raise ValidationError(
                f"File size ({file_size} bytes) exceeds limit ({active_limits.max_input_bytes} bytes).",
                details={"file_size": file_size, "max_bytes": active_limits.max_input_bytes},
            )

        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        raise FileSystemError(
            f"Failed to read file {path}: {e}",
            details={"path": str(path), "error": str(e)},
        ) from e

    return parse_json_string(content, limits=limits)
