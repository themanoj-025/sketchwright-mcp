"""Unit tests for Excalidraw scene serialization, stable IDs, and bindings."""

from sketchwright.excalidraw.bindings import generate_stable_id
from sketchwright.excalidraw.serializer import ExcalidrawSerializer
from sketchwright.layout.engine import LayoutEngine
from sketchwright.models.diagram import DiagramSpec
from sketchwright.models.elements import EdgeSpec, NodeSpec


def test_stable_id_generation_is_deterministic() -> None:
    id1 = generate_stable_id("shape", "user_service", salt="v1")
    id2 = generate_stable_id("shape", "user_service", salt="v1")
    assert id1 == id2
    assert len(id1) == 16


def test_serializer_generates_reciprocal_bindings() -> None:
    spec = DiagramSpec(
        title="Binding Test",
        nodes=[
            NodeSpec(id="a", label="Source Node", shape="rectangle"),
            NodeSpec(id="b", label="Target Node", shape="rounded_rectangle"),
        ],
        edges=[EdgeSpec(id="e1", source="a", target="b", label="connects")],
    )
    engine = LayoutEngine(spec)
    laid_out = engine.layout()

    serializer = ExcalidrawSerializer(spec, laid_out)
    scene = serializer.serialize()

    elements = scene["elements"]
    elem_by_id = {e["id"]: e for e in elements}

    # Find arrow
    arrows = [e for e in elements if e["type"] == "arrow"]
    assert len(arrows) == 1
    arrow = arrows[0]

    src_id = arrow["startBinding"]["elementId"]
    tgt_id = arrow["endBinding"]["elementId"]

    # Verify reciprocal binding on source shape
    src_elem = elem_by_id[src_id]
    assert any(b["id"] == arrow["id"] and b["type"] == "arrow" for b in src_elem["boundElements"])

    # Verify reciprocal binding on target shape
    tgt_elem = elem_by_id[tgt_id]
    assert any(b["id"] == arrow["id"] and b["type"] == "arrow" for b in tgt_elem["boundElements"])

    # Verify text container reciprocal bindings
    texts = [e for e in elements if e["type"] == "text" and e.get("containerId")]
    assert len(texts) == 2
    for t in texts:
        cont = elem_by_id[t["containerId"]]
        assert any(b["id"] == t["id"] and b["type"] == "text" for b in cont["boundElements"])


def test_cylinder_database_shape_serialized() -> None:
    spec = DiagramSpec(
        nodes=[NodeSpec(id="db", label="Postgres", shape="cylinder")],
    )
    laid_out = LayoutEngine(spec).layout()
    scene = ExcalidrawSerializer(spec, laid_out).serialize()

    db_shapes = [e for e in scene["elements"] if e.get("customData", {}).get("shape") == "cylinder"]
    assert len(db_shapes) == 1
    assert db_shapes[0]["roundness"] == {"type": 3}
