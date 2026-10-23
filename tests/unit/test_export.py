"""Unit tests for atomic file persistence and SVG export."""

from pathlib import Path

import pytest

from sketchwright.errors import FileSystemError
from sketchwright.excalidraw.export import export_svg, write_excalidraw_file


def test_atomic_write_excalidraw_file(tmp_path: Path) -> None:
    scene = {"type": "excalidraw", "version": 2, "elements": []}
    out_file = tmp_path / "diagram.excalidraw"
    written = write_excalidraw_file(scene, out_file)
    assert written.is_file()
    assert '"type": "excalidraw"' in written.read_text(encoding="utf-8")


def test_overwrite_protection_enforced(tmp_path: Path) -> None:
    scene = {"type": "excalidraw", "version": 2, "elements": []}
    out_file = tmp_path / "existing.excalidraw"
    out_file.write_text("pre-existing content", encoding="utf-8")

    # Overwrite disabled by default -> must raise FileSystemError
    with pytest.raises(FileSystemError) as exc:
        write_excalidraw_file(scene, out_file, overwrite=False)
    assert "already exists" in str(exc.value)

    # Overwrite enabled -> succeeds
    write_excalidraw_file(scene, out_file, overwrite=True)
    assert '"type": "excalidraw"' in out_file.read_text(encoding="utf-8")


def test_export_svg_structure() -> None:
    scene = {
        "type": "excalidraw",
        "version": 2,
        "elements": [
            {
                "id": "r1",
                "type": "rectangle",
                "x": 10.0,
                "y": 20.0,
                "width": 100.0,
                "height": 50.0,
                "strokeColor": "#1e1e1e",
                "backgroundColor": "#e7f5ff",
            },
            {
                "id": "t1",
                "type": "text",
                "x": 20.0,
                "y": 30.0,
                "width": 80.0,
                "height": 30.0,
                "text": "Hello <World>",
                "fontSize": 16,
                "textAlign": "center",
            },
        ],
    }
    svg = export_svg(scene)
    assert svg.startswith("<svg")
    assert svg.endswith("</svg>")
    assert "<rect" in svg
    assert "<text" in svg
    # XML escaping
    assert "Hello &lt;World&gt;" in svg


def test_export_svg_shapes_and_arrows() -> None:
    scene = {
        "type": "excalidraw",
        "version": 2,
        "elements": [
            {"id": "e1", "type": "ellipse", "x": 0, "y": 0, "width": 50, "height": 50},
            {"id": "d1", "type": "diamond", "x": 60, "y": 0, "width": 40, "height": 40},
            {
                "id": "a1",
                "type": "arrow",
                "x": 0,
                "y": 0,
                "width": 50,
                "height": 50,
                "points": [[0, 0], [50, 50]],
                "endArrowhead": "arrow",
            },
        ],
    }
    svg = export_svg(scene)
    assert "<ellipse" in svg
    assert "<polygon" in svg
    assert "<path" in svg


def test_write_svg_file_atomic(tmp_path: Path) -> None:
    from sketchwright.excalidraw.export import write_svg_file

    scene = {"type": "excalidraw", "version": 2, "elements": []}
    out_file = tmp_path / "test.svg"
    written = write_svg_file(scene, out_file)
    assert written.is_file()
    assert "<svg" in written.read_text(encoding="utf-8")


def test_export_svg_multiline_and_unicode() -> None:
    scene = {
        "type": "excalidraw",
        "version": 2,
        "elements": [
            {
                "id": "t_multi",
                "type": "text",
                "x": 10.0,
                "y": 20.0,
                "width": 100.0,
                "height": 60.0,
                "text": "Line 1: サービス\nLine 2: 🚀 Rocket",
                "fontSize": 14,
                "textAlign": "center",
            }
        ],
    }
    svg = export_svg(scene)
    assert "<tspan" in svg
    assert "サービス" in svg
    assert "🚀 Rocket" in svg


def test_export_svg_empty_and_deleted_elements() -> None:
    scene = {
        "type": "excalidraw",
        "version": 2,
        "elements": [
            {"id": "del1", "type": "rectangle", "isDeleted": True},
            "not_a_dict_element",  # malformed element ignored gracefully
        ],
    }
    svg = export_svg(scene)
    assert "<svg" in svg
    assert "</svg>" in svg


def test_path_traversal_blocked_by_enforce_boundary(tmp_path: Path) -> None:
    from sketchwright.excalidraw.export import validate_safe_output_path

    workspace = tmp_path / "workspace"
    workspace.mkdir()
    traversal_path = workspace / ".." / "escaped.excalidraw"

    with pytest.raises(FileSystemError) as exc:
        validate_safe_output_path(traversal_path, enforce_boundary=True, allowed_root=workspace)
    assert "resolves outside authorized directory" in str(exc.value)
