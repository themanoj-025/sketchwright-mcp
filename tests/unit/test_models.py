"""Unit tests for domain models, validation logic, and resource limits."""

import pytest

from sketchwright.config import Limits
from sketchwright.models.diagram import DiagramSpec
from sketchwright.models.elements import EdgeSpec, LayoutConfig, NodeSpec
from sketchwright.models.validation import validate_diagram_spec, validate_raw_input


def test_valid_minimal_diagram_spec() -> None:
    spec = DiagramSpec(
        nodes=[NodeSpec(id="n1", label="Node 1")],
        edges=[],
    )
    result = validate_diagram_spec(spec)
    assert result.is_valid
    assert len(result.errors) == 0
    assert result.stats["nodes"] == 1


def test_duplicate_node_ids_detected() -> None:
    raw = {
        "nodes": [
            {"id": "a", "label": "First"},
            {"id": "a", "label": "Second"},
        ]
    }
    result, spec = validate_raw_input(raw)
    assert not result.is_valid
    assert spec is None
    assert any("Duplicate node IDs" in err for err in result.errors)


def test_dangling_edge_target_rejected() -> None:
    raw = {
        "nodes": [{"id": "a", "label": "A"}],
        "edges": [{"id": "e1", "source": "a", "target": "b"}],
    }
    result, spec = validate_raw_input(raw)
    assert not result.is_valid
    assert any("unresolved target endpoint 'b'" in err for err in result.errors)


def test_duplicate_edge_ids_detected() -> None:
    raw = {
        "nodes": [{"id": "a"}, {"id": "b"}],
        "edges": [
            {"id": "e1", "source": "a", "target": "b"},
            {"id": "e1", "source": "b", "target": "a"},
        ],
    }
    result, spec = validate_raw_input(raw)
    assert not result.is_valid
    assert any("Duplicate edge IDs" in err for err in result.errors)


def test_resource_limits_enforced() -> None:
    limits = Limits(max_nodes=2, max_edges=1)
    spec = DiagramSpec(
        nodes=[NodeSpec(id=f"n{i}") for i in range(3)],
        edges=[EdgeSpec(id=f"e{i}", source="n0", target="n1") for i in range(2)],
    )
    result = validate_diagram_spec(spec, limits=limits)
    assert not result.is_valid
    assert any("Node count 3 exceeds" in err for err in result.errors)
    assert any("Edge count 2 exceeds" in err for err in result.errors)


def test_finite_numeric_validation() -> None:
    with pytest.raises(ValueError):
        LayoutConfig(node_spacing=float("nan"))

    with pytest.raises(ValueError):
        LayoutConfig(rank_spacing=float("inf"))


def test_invalid_shape_name_rejected() -> None:
    raw = {"nodes": [{"id": "a", "shape": "hexagon"}]}
    result, spec = validate_raw_input(raw)
    assert not result.is_valid
    assert any("shape" in err for err in result.errors)


def test_self_loop_warning() -> None:
    raw = {
        "nodes": [{"id": "a"}],
        "edges": [{"id": "e1", "source": "a", "target": "a"}],
    }
    result, spec = validate_raw_input(raw)
    assert result.is_valid
    assert any("self-loop" in w for w in result.warnings)
