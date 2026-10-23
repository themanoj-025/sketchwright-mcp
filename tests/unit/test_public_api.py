"""Unit tests verifying the stable public Python API (Section 11)."""

from pathlib import Path

import pytest

from sketchwright import (
    DiagramSpec,
    ValidationError,
    export_diagram,
    generate_diagram,
    get_capabilities,
    layout_diagram,
    update_diagram,
    validate_diagram,
)
from sketchwright.models.elements import NodeSpec


def test_public_generate_diagram_from_dict() -> None:
    spec_dict = {
        "title": "Public API Test",
        "nodes": [{"id": "a", "label": "Node A"}, {"id": "b", "label": "Node B"}],
        "edges": [{"id": "e1", "source": "a", "target": "b"}],
    }
    result = generate_diagram(spec_dict)
    assert result.validation.is_valid
    assert len(result.scene["elements"]) > 0


def test_public_generate_diagram_from_dsl() -> None:
    dsl = """
    title: DSL API Test
    direction: TB
    [app: rectangle: App Service]
    [db: cylinder: PostgreSQL]
    app -> db: queries
    """
    result = generate_diagram(dsl)
    assert result.validation.is_valid
    assert len(result.laid_out.nodes) == 2
    assert len(result.laid_out.edges) == 1


def test_public_generate_diagram_from_model() -> None:
    spec = DiagramSpec(nodes=[NodeSpec(id="x", label="X")])
    result = generate_diagram(spec)
    assert result.validation.is_valid


def test_public_generate_diagram_file_export(tmp_path: Path) -> None:
    out_excal = tmp_path / "test.excalidraw"
    out_svg = tmp_path / "test.svg"

    spec = {"nodes": [{"id": "n1"}]}
    generate_diagram(spec, output_path=out_excal)
    assert out_excal.is_file()

    generate_diagram(spec, output_path=out_svg, format="svg")
    assert out_svg.is_file()
    assert "<svg" in out_svg.read_text(encoding="utf-8")


def test_public_validate_diagram_both() -> None:
    spec = {"nodes": [{"id": "n1"}]}
    gen = generate_diagram(spec)

    report = validate_diagram(specification=spec, scene=gen.scene)
    assert report["is_valid"] is True
    assert "specification" in report
    assert "scene" in report


def test_public_validate_diagram_errors() -> None:
    with pytest.raises(ValidationError):
        validate_diagram()  # None provided


def test_public_layout_diagram() -> None:
    laid_out = layout_diagram({"nodes": [{"id": "n1"}, {"id": "n2"}]})
    assert len(laid_out.nodes) == 2
    assert laid_out.canvas_rect.width > 0


def test_public_export_diagram(tmp_path: Path) -> None:
    spec = {"nodes": [{"id": "n"}]}
    gen = generate_diagram(spec)
    out_path = tmp_path / "manual_export.excalidraw"

    written = export_diagram(gen.scene, out_path)
    assert written.is_file()


def test_public_update_diagram() -> None:
    base = {"nodes": [{"id": "a", "label": "Start"}]}
    patch = {"add_nodes": [{"id": "b", "label": "End"}], "add_edges": [{"id": "e", "source": "a", "target": "b"}]}
    result = update_diagram(base, patch)
    assert result.validation.is_valid
    assert len(result.laid_out.nodes) == 2
    assert len(result.laid_out.edges) == 1


def test_public_get_capabilities() -> None:
    caps = get_capabilities()
    assert caps["product"] == "Sketchwright"
    assert "rectangle" in caps["supported_shapes"]
