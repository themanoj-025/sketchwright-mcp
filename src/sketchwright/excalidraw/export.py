"""Safe atomic file persistence and SVG export for Excalidraw scenes."""

from __future__ import annotations

import json
import os
import uuid
import xml.sax.saxutils as saxutils
from pathlib import Path
from typing import Any, Union

from sketchwright.errors import FileSystemError


def write_excalidraw_file(
    scene: dict[str, Any],
    output_path: Union[str, Path],
    overwrite: bool = False,
) -> Path:
    """Safely write an Excalidraw scene to a local file using atomic rename."""
    target = Path(output_path).resolve()

    if target.exists() and not overwrite:
        raise FileSystemError(
            f"Destination file already exists: {target}. Use --overwrite to allow replacing it.",
            details={"path": str(target)},
        )

    parent_dir = target.parent
    try:
        parent_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise FileSystemError(
            f"Failed to create parent directory for {target}: {e}",
            details={"path": str(target), "error": str(e)},
        ) from e

    # Atomic write to temporary file first
    temp_file = parent_dir / f".{target.name}.{uuid.uuid4().hex[:8]}.tmp"
    try:
        content = json.dumps(scene, indent=2, ensure_ascii=False)
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())

        # Atomic replacement
        os.replace(temp_file, target)
    except Exception as e:
        if temp_file.exists():
            try:
                temp_file.unlink()
            except OSError:
                pass
        raise FileSystemError(
            f"Failed to write scene file {target}: {e}",
            details={"path": str(target), "error": str(e)},
        ) from e

    return target


def export_svg(scene: dict[str, Any]) -> str:
    """Export an Excalidraw scene as a standalone, valid SVG document."""
    elements = scene.get("elements", [])
    if not elements:
        return '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"></svg>'

    # Compute bounding box
    min_x = float("inf")
    min_y = float("inf")
    max_x = float("-inf")
    max_y = float("-inf")

    for elem in elements:
        if not isinstance(elem, dict) or elem.get("isDeleted"):
            continue
        x = elem.get("x", 0.0)
        y = elem.get("y", 0.0)
        w = elem.get("width", 0.0)
        h = elem.get("height", 0.0)
        min_x = min(min_x, x)
        min_y = min(min_y, y)
        max_x = max(max_x, x + w)
        max_y = max(max_y, y + h)

    padding = 40.0
    vb_x = round(min_x - padding, 1)
    vb_y = round(min_y - padding, 1)
    vb_w = round(max(100.0, (max_x - min_x) + 2 * padding), 1)
    vb_h = round(max(100.0, (max_y - min_y) + 2 * padding), 1)

    bg_color = scene.get("appState", {}).get("viewBackgroundColor", "#ffffff")

    svg_parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb_x} {vb_y} {vb_w} {vb_h}" width="{vb_w}" height="{vb_h}">',
        "  <defs>",
        '    <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#495057" />',
        "    </marker>",
        "  </defs>",
        f'  <rect x="{vb_x}" y="{vb_y}" width="{vb_w}" height="{vb_h}" fill="{bg_color}" />',
    ]

    for elem in elements:
        if not isinstance(elem, dict) or elem.get("isDeleted"):
            continue

        etype = elem.get("type")
        x = elem.get("x", 0.0)
        y = elem.get("y", 0.0)
        w = elem.get("width", 0.0)
        h = elem.get("height", 0.0)
        stroke = elem.get("strokeColor", "#1e1e1e")
        fill = elem.get("backgroundColor", "transparent")
        stroke_w = elem.get("strokeWidth", 2)

        if etype == "rectangle":
            rx = 8 if elem.get("roundness") else 0
            svg_parts.append(
                f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_w}" />'
            )
        elif etype == "ellipse":
            cx = round(x + w / 2.0, 1)
            cy = round(y + h / 2.0, 1)
            rx = round(w / 2.0, 1)
            ry = round(h / 2.0, 1)
            svg_parts.append(
                f'  <ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_w}" />'
            )
        elif etype == "diamond":
            p_top = f"{round(x + w / 2.0, 1)},{y}"
            p_right = f"{round(x + w, 1)},{round(y + h / 2.0, 1)}"
            p_bottom = f"{round(x + w / 2.0, 1)},{round(y + h, 1)}"
            p_left = f"{x},{round(y + h / 2.0, 1)}"
            points = f"{p_top} {p_right} {p_bottom} {p_left}"
            svg_parts.append(
                f'  <polygon points="{points}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_w}" />'
            )
        elif etype == "arrow":
            rel_points = elem.get("points", [])
            if rel_points:
                path_d: list[str] = []
                for idx, pt in enumerate(rel_points):
                    px = round(x + pt[0], 1)
                    py = round(y + pt[1], 1)
                    cmd = "M" if idx == 0 else "L"
                    path_d.append(f"{cmd} {px} {py}")
                d_str = " ".join(path_d)
                marker = ' marker-end="url(#arrow)"' if elem.get("endArrowhead") == "arrow" else ""
                svg_parts.append(
                    f'  <path d="{d_str}" fill="none" stroke="{stroke}" stroke-width="{stroke_w}"{marker} />'
                )
        elif etype == "text":
            raw_text = elem.get("text", "")
            escaped_text = saxutils.escape(raw_text)
            fsize = elem.get("fontSize", 16)
            align = elem.get("textAlign", "center")
            anchor = "middle" if align == "center" else ("start" if align == "left" else "end")

            text_x = round(x + w / 2.0, 1) if align == "center" else x
            text_y = round(y + h / 2.0 + fsize * 0.35, 1)

            svg_parts.append(
                f'  <text x="{text_x}" y="{text_y}" font-family="sans-serif" font-size="{fsize}" fill="{stroke}" text-anchor="{anchor}">{escaped_text}</text>'
            )

    svg_parts.append("</svg>")
    return "\n".join(svg_parts)


def write_svg_file(
    scene: dict[str, Any],
    output_path: Union[str, Path],
    overwrite: bool = False,
) -> Path:
    """Export scene to an SVG file safely with atomic write."""
    target = Path(output_path).resolve()
    if target.exists() and not overwrite:
        raise FileSystemError(f"File exists: {target}. Use --overwrite to replace.")

    svg_content = export_svg(scene)
    temp_file = target.parent / f".{target.name}.{uuid.uuid4().hex[:8]}.tmp"
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(svg_content)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_file, target)
    except Exception as e:
        if temp_file.exists():
            try:
                temp_file.unlink()
            except OSError:
                pass
        raise FileSystemError(f"Failed to write SVG file {target}: {e}") from e

    return target
