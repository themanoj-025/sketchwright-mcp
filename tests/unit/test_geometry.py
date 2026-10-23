"""Unit tests for geometry, bounding boxes, ray-shape anchors, and text sizing."""

from sketchwright.layout.geometry import (
    Point,
    Rect,
    approximate_text_dimensions,
    get_shape_boundary_anchor,
)


def test_point_distance_and_offset() -> None:
    p1 = Point(0.0, 0.0)
    p2 = Point(3.0, 4.0)
    assert p1.distance_to(p2) == 5.0
    p3 = p1.offset(10.0, 20.0)
    assert p3.x == 10.0 and p3.y == 20.0


def test_rect_properties_and_intersection() -> None:
    r1 = Rect(x=0.0, y=0.0, width=100.0, height=50.0)
    assert r1.left == 0.0
    assert r1.right == 100.0
    assert r1.top == 0.0
    assert r1.bottom == 50.0
    assert r1.center_x == 50.0
    assert r1.center_y == 25.0

    # Overlapping rect
    r2 = Rect(x=50.0, y=25.0, width=100.0, height=50.0)
    assert r1.intersects(r2)

    # Disjoint rect
    r3 = Rect(x=200.0, y=200.0, width=50.0, height=50.0)
    assert not r1.intersects(r3)


def test_text_dimension_approximation_multiline() -> None:
    w1, h1 = approximate_text_dimensions("Short", font_size=16, shape="rectangle")
    w2, h2 = approximate_text_dimensions(
        "Line 1\nMuch Longer Second Line Here\nLine 3", font_size=16, shape="rectangle"
    )
    assert w2 > w1
    assert h2 > h1


def test_shape_boundary_anchors() -> None:
    rect = Rect(x=100.0, y=100.0, width=100.0, height=60.0)
    # Target to the right
    anchor_r = get_shape_boundary_anchor(rect, Point(300.0, 130.0), shape="rectangle")
    assert anchor_r.x == 200.0  # right edge
    assert anchor_r.y == 130.0  # center_y

    # Target to the left
    anchor_l = get_shape_boundary_anchor(rect, Point(0.0, 130.0), shape="rectangle")
    assert anchor_l.x == 100.0  # left edge
    assert anchor_l.y == 130.0

    # Preferred side override
    anchor_top = get_shape_boundary_anchor(rect, Point(300.0, 130.0), preferred_side="T")
    assert anchor_top.y == 100.0  # top edge
