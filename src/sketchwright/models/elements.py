"""Element specifications and domain models for nodes, edges, and styling."""

from __future__ import annotations

import math
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

ShapeType = Literal[
    "rectangle",
    "rounded_rectangle",
    "ellipse",
    "diamond",
    "cylinder",
    "text",
]

EdgeKind = Literal["directed", "undirected", "bidirectional"]
LayoutAlgorithm = Literal["layered", "grid", "tree"]
LayoutDirection = Literal["LR", "RL", "TB", "BT"]


class LayoutConfig(BaseModel):
    """Layout engine settings."""

    model_config = ConfigDict(extra="forbid")

    algorithm: LayoutAlgorithm = "layered"
    direction: LayoutDirection = "LR"
    node_spacing: float = Field(default=80.0, ge=10.0, le=2000.0)
    rank_spacing: float = Field(default=120.0, ge=10.0, le=2000.0)
    padding: float = Field(default=40.0, ge=0.0, le=1000.0)

    @field_validator("node_spacing", "rank_spacing", "padding")
    @classmethod
    def check_finite(cls, v: float) -> float:
        if not math.isfinite(v):
            raise ValueError("Numeric layout dimensions must be finite numbers.")
        return v


class StyleConfig(BaseModel):
    """Visual theme and element styling properties."""

    model_config = ConfigDict(extra="forbid")

    theme: Literal["light", "dark"] = "light"
    font_size: int = Field(default=16, ge=8, le=72)
    stroke_width: int = Field(default=2, ge=1, le=10)
    stroke_color: Optional[str] = None
    background_color: Optional[str] = None
    roughness: int = Field(default=1, ge=0, le=2)


class NodeSpec(BaseModel):
    """Specification of a single diagram node."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1, max_length=128)
    label: str = Field(default="", max_length=512)
    shape: ShapeType = "rectangle"
    group: Optional[str] = None
    width: Optional[float] = Field(default=None, gt=0, le=50000.0)
    height: Optional[float] = Field(default=None, gt=0, le=50000.0)
    style: Optional[StyleConfig] = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        v_stripped = v.strip()
        if not v_stripped:
            raise ValueError("Node ID cannot be empty or pure whitespace.")
        return v_stripped


class EdgeSpec(BaseModel):
    """Specification of a directed or undirected connection between two nodes."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1, max_length=128)
    source: str = Field(min_length=1, max_length=128)
    target: str = Field(min_length=1, max_length=128)
    label: Optional[str] = Field(default=None, max_length=256)
    kind: EdgeKind = "directed"
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("id", "source", "target")
    @classmethod
    def validate_ids(cls, v: str) -> str:
        v_stripped = v.strip()
        if not v_stripped:
            raise ValueError("Edge ID, source, and target cannot be empty.")
        return v_stripped


class GroupSpec(BaseModel):
    """Specification of a visual container or logical node group."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1, max_length=128)
    label: Optional[str] = Field(default=None, max_length=256)
    metadata: dict[str, Any] = Field(default_factory=dict)
