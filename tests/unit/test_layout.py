"""Unit tests for layout algorithms, cycle breaking, rankings, and directions."""

from sketchwright.layout.engine import LayoutEngine
from sketchwright.models.diagram import DiagramSpec
from sketchwright.models.elements import EdgeSpec, LayoutConfig, NodeSpec


def test_layered_layout_non_overlapping_nodes() -> None:
    spec = DiagramSpec(
        nodes=[
            NodeSpec(id="a", label="Alpha"),
            NodeSpec(id="b", label="Beta"),
            NodeSpec(id="c", label="Gamma"),
        ],
        edges=[
            EdgeSpec(id="e1", source="a", target="b"),
            EdgeSpec(id="e2", source="b", target="c"),
        ],
        layout=LayoutConfig(algorithm="layered", direction="LR", node_spacing=50.0, rank_spacing=100.0),
    )
    engine = LayoutEngine(spec)
    laid_out = engine.layout()

    rect_a = laid_out.nodes["a"].rect
    rect_b = laid_out.nodes["b"].rect
    rect_c = laid_out.nodes["c"].rect

    # LR direction: a.x < b.x < c.x
    assert rect_a.right <= rect_b.left
    assert rect_b.right <= rect_c.left
    assert len(laid_out.stats["overlaps"]) == 0


def test_layered_layout_cyclic_graph_terminates() -> None:
    # 3-node cycle: a -> b -> c -> a
    spec = DiagramSpec(
        nodes=[
            NodeSpec(id="a", label="A"),
            NodeSpec(id="b", label="B"),
            NodeSpec(id="c", label="C"),
        ],
        edges=[
            EdgeSpec(id="e1", source="a", target="b"),
            EdgeSpec(id="e2", source="b", target="c"),
            EdgeSpec(id="e3", source="c", target="a"),
        ],
        layout=LayoutConfig(direction="LR"),
    )
    engine = LayoutEngine(spec)
    laid_out = engine.layout()

    # Must complete and position all 3 nodes
    assert len(laid_out.nodes) == 3
    assert len(laid_out.edges) == 3


def test_layout_directions() -> None:
    for direction in ("LR", "RL", "TB", "BT"):
        spec = DiagramSpec(
            nodes=[
                NodeSpec(id="src", label="Source"),
                NodeSpec(id="tgt", label="Target"),
            ],
            edges=[EdgeSpec(id="e", source="src", target="tgt")],
            layout=LayoutConfig(direction=direction),  # type: ignore[arg-type]
        )
        engine = LayoutEngine(spec)
        laid_out = engine.layout()
        r_src = laid_out.nodes["src"].rect
        r_tgt = laid_out.nodes["tgt"].rect

        if direction == "LR":
            assert r_src.right <= r_tgt.left
        elif direction == "RL":
            assert r_tgt.right <= r_src.left
        elif direction == "TB":
            assert r_src.bottom <= r_tgt.top
        elif direction == "BT":
            assert r_tgt.bottom <= r_src.top


def test_disconnected_components_handling() -> None:
    spec = DiagramSpec(
        nodes=[
            NodeSpec(id="c1_1"),
            NodeSpec(id="c1_2"),
            NodeSpec(id="c2_1"),
            NodeSpec(id="c2_2"),
        ],
        edges=[
            EdgeSpec(id="e1", source="c1_1", target="c1_2"),
            EdgeSpec(id="e2", source="c2_1", target="c2_2"),
        ],
        layout=LayoutConfig(direction="LR"),
    )
    engine = LayoutEngine(spec)
    laid_out = engine.layout()
    assert len(laid_out.nodes) == 4
    assert len(laid_out.stats["overlaps"]) == 0


def test_grid_layout_execution() -> None:
    spec = DiagramSpec(
        nodes=[NodeSpec(id=f"n{i}") for i in range(9)],
        layout=LayoutConfig(algorithm="grid"),
    )
    engine = LayoutEngine(spec)
    laid_out = engine.layout()
    assert len(laid_out.nodes) == 9
    assert len(laid_out.stats["overlaps"]) == 0
