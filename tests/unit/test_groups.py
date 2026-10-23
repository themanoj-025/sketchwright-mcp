"""Unit tests for visual grouping and container serialization (Section 8)."""

from sketchwright.excalidraw.serializer import ExcalidrawSerializer
from sketchwright.layout.engine import LayoutEngine
from sketchwright.models.diagram import DiagramSpec
from sketchwright.models.elements import GroupSpec, NodeSpec


def test_group_containers_and_group_ids_serialized() -> None:
    spec = DiagramSpec(
        title="Grouped Architecture",
        groups=[
            GroupSpec(id="backend", label="Backend Services"),
        ],
        nodes=[
            NodeSpec(id="api", label="API Gateway", group="backend"),
            NodeSpec(id="auth", label="Auth Service", group="backend"),
            NodeSpec(id="client", label="Browser Client"),  # ungrouped
        ],
    )

    laid_out = LayoutEngine(spec).layout()
    serializer = ExcalidrawSerializer(spec, laid_out)
    scene = serializer.serialize()

    elements = scene["elements"]

    # Verify group container box element is generated
    group_boxes = [e for e in elements if e.get("customData", {}).get("isGroupContainer")]
    assert len(group_boxes) == 1
    box = group_boxes[0]
    assert box["type"] == "rectangle"
    assert box["strokeStyle"] == "dashed"
    assert len(box["groupIds"]) == 1

    # Verify member nodes have groupIds populated
    api_elem = [e for e in elements if e.get("customData", {}).get("nodeId") == "api"][0]
    auth_elem = [e for e in elements if e.get("customData", {}).get("nodeId") == "auth"][0]
    client_elem = [e for e in elements if e.get("customData", {}).get("nodeId") == "client"][0]

    assert len(api_elem["groupIds"]) == 1
    assert api_elem["groupIds"] == auth_elem["groupIds"]
    assert len(client_elem["groupIds"]) == 0

    # Verify group container encompasses member nodes
    assert box["x"] <= api_elem["x"]
    assert box["y"] <= api_elem["y"]
    assert box["x"] + box["width"] >= api_elem["x"] + api_elem["width"]
    assert box["y"] + box["height"] >= api_elem["y"] + api_elem["height"]

    # Verify group label text element exists
    group_labels = [e for e in elements if e["type"] == "text" and e.get("text") == "Backend Services"]
    assert len(group_labels) == 1
    assert group_labels[0]["groupIds"] == box["groupIds"]
