"""Unit tests for incremental diagram updates (Section 8.1)."""

import pytest

from sketchwright.engine.updater import DiagramUpdatePatch, update_diagram_spec
from sketchwright.errors import ValidationError
from sketchwright.models.diagram import DiagramSpec
from sketchwright.models.elements import EdgeSpec, NodeSpec


def test_incremental_add_nodes_and_edges() -> None:
    base = DiagramSpec(
        title="Base Architecture",
        nodes=[NodeSpec(id="api", label="API Gateway")],
        edges=[],
    )

    patch = DiagramUpdatePatch(
        add_nodes=[NodeSpec(id="db", label="Database", shape="cylinder")],
        add_edges=[EdgeSpec(id="e1", source="api", target="db", label="query")],
    )

    updated = update_diagram_spec(base, patch)
    assert len(updated.nodes) == 2
    assert len(updated.edges) == 1
    assert updated.edges[0].source == "api"
    assert updated.edges[0].target == "db"


def test_incremental_update_node_properties() -> None:
    base = DiagramSpec(
        nodes=[NodeSpec(id="auth", label="Auth Service", shape="rectangle")],
    )

    patch = {
        "update_nodes": [
            {"id": "auth", "label": "OAuth2 Gateway", "shape": "rounded_rectangle"},
        ],
    }

    updated = update_diagram_spec(base, patch)
    assert len(updated.nodes) == 1
    assert updated.nodes[0].label == "OAuth2 Gateway"
    assert updated.nodes[0].shape == "rounded_rectangle"


def test_incremental_rename_node_propagates_to_edges() -> None:
    base = DiagramSpec(
        nodes=[
            NodeSpec(id="client", label="Client"),
            NodeSpec(id="old_srv", label="Server"),
        ],
        edges=[EdgeSpec(id="e1", source="client", target="old_srv", label="HTTP")],
    )

    patch = {
        "update_nodes": [
            {"id": "old_srv", "new_id": "new_srv", "label": "Upgraded Server"},
        ],
    }

    updated = update_diagram_spec(base, patch)
    node_ids = {n.id for n in updated.nodes}
    assert "new_srv" in node_ids
    assert "old_srv" not in node_ids

    # Edge endpoints must have updated
    assert updated.edges[0].source == "client"
    assert updated.edges[0].target == "new_srv"


def test_incremental_remove_node_cascades_pruning_edges() -> None:
    base = DiagramSpec(
        nodes=[
            NodeSpec(id="a", label="A"),
            NodeSpec(id="b", label="B"),
            NodeSpec(id="c", label="C"),
        ],
        edges=[
            EdgeSpec(id="e_ab", source="a", target="b"),
            EdgeSpec(id="e_bc", source="b", target="c"),
        ],
    )

    patch = {"remove_nodes": ["b"]}
    updated = update_diagram_spec(base, patch)

    assert len(updated.nodes) == 2
    assert {n.id for n in updated.nodes} == {"a", "c"}
    # All edges touching 'b' must have been automatically pruned
    assert len(updated.edges) == 0


def test_incremental_label_matching_fallback() -> None:
    base = DiagramSpec(
        nodes=[
            NodeSpec(id="srv_1", label="Unique Worker"),
            NodeSpec(id="srv_2", label="Cache Layer"),
        ],
    )

    # Update by label instead of ID
    patch = {
        "update_nodes": [
            {"label": "Unique Worker", "shape": "diamond"},
        ],
    }
    updated = update_diagram_spec(base, patch)
    node = [n for n in updated.nodes if n.id == "srv_1"][0]
    assert node.shape == "diamond"


def test_incremental_ambiguous_label_matching_rejected() -> None:
    base = DiagramSpec(
        nodes=[
            NodeSpec(id="srv_1", label="Worker"),
            NodeSpec(id="srv_2", label="Worker"),
        ],
    )

    # Attempting to target ambiguous label 'Worker' must raise ValidationError
    patch = {
        "update_nodes": [
            {"label": "Worker", "shape": "diamond"},
        ],
    }
    with pytest.raises(ValidationError) as exc:
        update_diagram_spec(base, patch)
    assert "Ambiguous node reference 'Worker'" in str(exc.value)


def test_incremental_preserves_unrelated_elements() -> None:
    base = DiagramSpec(
        title="System Architecture",
        nodes=[
            NodeSpec(id="preserved1", label="Keep Me"),
            NodeSpec(id="preserved2", label="Keep Me Too"),
        ],
        edges=[EdgeSpec(id="keep_edge", source="preserved1", target="preserved2")],
        metadata={"author": "Team A"},
    )

    patch = {
        "add_nodes": [{"id": "new_node", "label": "New"}],
    }
    updated = update_diagram_spec(base, patch)

    assert len(updated.nodes) == 3
    assert len(updated.edges) == 1
    assert updated.metadata == {"author": "Team A"}
    assert updated.title == "System Architecture"
