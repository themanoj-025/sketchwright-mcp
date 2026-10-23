"""Integration tests verifying the complete end-to-end diagram generation pipeline."""

import json
from pathlib import Path

from sketchwright import export_diagram, generate_diagram, validate_diagram

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


def test_pipeline_architecture_fixture() -> None:
    path = FIXTURES_DIR.parent.parent / "examples" / "architecture.json"
    spec_data = json.loads(path.read_text(encoding="utf-8"))

    result = generate_diagram(spec_data)
    assert result.validation.is_valid
    assert len(result.scene["elements"]) > 0

    # Ensure elements include 4 shapes + 4 texts + 3 arrows + 3 edge labels + 1 title
    arrows = [e for e in result.scene["elements"] if e["type"] == "arrow"]
    assert len(arrows) == 3


def test_pipeline_flowchart_fixture() -> None:
    path = FIXTURES_DIR.parent.parent / "examples" / "flowchart.json"
    spec_data = json.loads(path.read_text(encoding="utf-8"))

    result = generate_diagram(spec_data)
    assert result.validation.is_valid
    assert result.laid_out.canvas_rect.height > 0


def test_pipeline_cyclic_fixture() -> None:
    path = FIXTURES_DIR / "cyclic_graph.json"
    spec_data = json.loads(path.read_text(encoding="utf-8"))

    result = generate_diagram(spec_data)
    assert result.validation.is_valid
    assert len(result.laid_out.nodes) == 3


def test_pipeline_disconnected_fixture() -> None:
    path = FIXTURES_DIR / "disconnected_graph.json"
    spec_data = json.loads(path.read_text(encoding="utf-8"))

    result = generate_diagram(spec_data)
    assert result.validation.is_valid
    assert len(result.laid_out.nodes) == 5


def test_pipeline_unicode_fixture() -> None:
    path = FIXTURES_DIR / "unicode_labels.json"
    spec_data = json.loads(path.read_text(encoding="utf-8"))

    result = generate_diagram(spec_data)
    assert result.validation.is_valid
    # Check that unicode characters are preserved in elements
    texts = [e["text"] for e in result.scene["elements"] if e["type"] == "text"]
    assert any("🚀" in t for t in texts)
    assert any("客户端" in t for t in texts)


def test_public_api_export_and_validate(tmp_path: Path) -> None:
    spec = {"nodes": [{"id": "n1", "label": "API"}], "edges": []}
    result = generate_diagram(spec)
    out_file = tmp_path / "diagram.excalidraw"
    export_diagram(result.scene, out_file)

    val_report = validate_diagram(scene=result.scene)
    assert val_report["is_valid"]
    assert out_file.is_file()
