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
