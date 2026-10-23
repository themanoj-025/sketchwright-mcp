"""Deterministic 2D geometry models, ray-shape intersections, and text metric approximations."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

from sketchwright.models.elements import ShapeType


@dataclass(frozen=True)
class Point:
    """A 2D point with immutable coordinates."""

    x: float
    y: float

    def distance_to(self, other: Point) -> float:
        return math.hypot(self.x - other.x, self.y - other.y)

    def offset(self, dx: float, dy: float) -> Point:
        return Point(self.x + dx, self.y + dy)


@dataclass
class Rect:
    """A 2D axis-aligned bounding rectangle."""

    x: float
    y: float
    width: float
    height: float

    @property
    def left(self) -> float:
        return self.x

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def top(self) -> float:
        return self.y

    @property
    def bottom(self) -> float:
        return self.y + self.height

    @property
    def center_x(self) -> float:
        return self.x + self.width / 2.0

    @property
    def center_y(self) -> float:
        return self.y + self.height / 2.0

    @property
    def center(self) -> Point:
        return Point(self.center_x, self.center_y)

    def intersects(self, other: Rect, tolerance: float = 0.0) -> bool:
        """Check if this rectangle overlaps with another rectangle beyond tolerance."""
        return not (
            self.right <= other.left + tolerance
            or self.left >= other.right - tolerance
            or self.bottom <= other.top + tolerance
            or self.top >= other.bottom - tolerance
        )

    def contains(self, point: Point) -> bool:
        return self.left <= point.x <= self.right and self.top <= point.y <= self.bottom


def approximate_text_dimensions(
    text: str,
    font_size: int = 16,
    shape: ShapeType = "rectangle",
) -> tuple[float, float]:
    """Calculate deterministic approximated node dimensions based on text length and shape.

    Avoids external font dependencies while providing ample padding for readability.
    """
    if not text:
        text = " "

    lines = text.split("\n")
    max_line_len = max(len(line) for line in lines)
    line_count = len(lines)

    # Average character width approx: ~0.60 * font_size
    char_width = font_size * 0.62
    line_height = font_size * 1.35

    calc_width = max_line_len * char_width + 40.0
    calc_height = line_count * line_height + 30.0

    # Apply shape-specific minimums and aspect ratios
    if shape in ("rectangle", "rounded_rectangle"):
        w = max(120.0, calc_width)
        h = max(60.0, calc_height)
    elif shape == "cylinder":
        w = max(120.0, calc_width)
        h = max(75.0, calc_height + 15.0)  # Extra height for top cylinder cap
    elif shape == "ellipse":
        # Ellipse needs wider padding at corners
        w = max(140.0, calc_width * 1.25)
        h = max(70.0, calc_height * 1.25)
    elif shape == "diamond":
        # Diamond inscribed box requires sqrt(2) expansion
        diag = max(calc_width, calc_height) * 1.45
        w = max(110.0, diag)
        h = max(110.0, diag)
    elif shape == "text":
        w = max(60.0, calc_width - 20.0)
        h = max(30.0, calc_height - 10.0)
    else:
        w = max(120.0, calc_width)
        h = max(60.0, calc_height)

    # Round to 1 decimal place to eliminate floating point noise
    return round(w, 1), round(h, 1)


def get_shape_boundary_anchor(
    rect: Rect,
    target_point: Point,
    shape: ShapeType = "rectangle",
    preferred_side: Optional[str] = None,
) -> Point:
    """Calculate the precise contact point on a shape's perimeter facing target_point.

    Supports rectangle, rounded_rectangle, ellipse, diamond, cylinder, and preferred sides.
    """
    center = rect.center
    if preferred_side == "L":
        return Point(rect.left, center.y)
    if preferred_side == "R":
        return Point(rect.right, center.y)
    if preferred_side == "T":
        return Point(center.x, rect.top)
    if preferred_side == "B":
        return Point(center.x, rect.bottom)

    dx = target_point.x - center.x
    dy = target_point.y - center.y

    if abs(dx) < 1e-6 and abs(dy) < 1e-6:
        return Point(rect.right, center.y)

    if shape in ("rectangle", "rounded_rectangle", "cylinder", "text"):
        # Ray-rectangle intersection
        half_w = rect.width / 2.0
        half_h = rect.height / 2.0
        scale_x = half_w / abs(dx) if dx != 0 else float("inf")
        scale_y = half_h / abs(dy) if dy != 0 else float("inf")
        scale = min(scale_x, scale_y)
        return Point(round(center.x + dx * scale, 1), round(center.y + dy * scale, 1))

    elif shape == "ellipse":
        # Ray-ellipse intersection: (x/a)^2 + (y/b)^2 = 1
        a = rect.width / 2.0
        b = rect.height / 2.0
        denom = math.sqrt((dx * b) ** 2 + (dy * a) ** 2)
        if denom == 0:
            return Point(center.x + a, center.y)
        scale = (a * b) / denom
        return Point(round(center.x + dx * scale, 1), round(center.y + dy * scale, 1))

    elif shape == "diamond":
        # Diamond is |x/half_w| + |y/half_h| = 1
        half_w = rect.width / 2.0
        half_h = rect.height / 2.0
        denom = abs(dx) / half_w + abs(dy) / half_h
        scale = 1.0 / denom if denom > 0 else 1.0
        return Point(round(center.x + dx * scale, 1), round(center.y + dy * scale, 1))

    # Default to rectangle anchor
    half_w = rect.width / 2.0
    half_h = rect.height / 2.0
    scale = min(half_w / abs(dx) if dx != 0 else 1.0, half_h / abs(dy) if dy != 0 else 1.0)
    return Point(round(center.x + dx * scale, 1), round(center.y + dy * scale, 1))
