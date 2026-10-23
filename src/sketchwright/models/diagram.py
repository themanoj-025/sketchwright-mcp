"""Top-level canonical diagram specification model."""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from sketchwright.models.elements import (
    EdgeSpec,
    GroupSpec,
    LayoutConfig,
    NodeSpec,
    StyleConfig,
)


class DiagramOptions(BaseModel):
    """Runtime options influencing layout and generation."""

    model_config = ConfigDict(extra="forbid")

    deterministic: bool = True
    validate_scene: bool = True
    curve_style: Literal["straight", "orthogonal", "curved"] = "orthogonal"


class DiagramSpec(BaseModel):
    """Canonical, versioned diagram specification.

    This represents the authoritative contract for structured diagram inputs.
    """

    model_config = ConfigDict(extra="forbid")

    schema_version: str = Field(default="1.0", pattern=r"^1\.[0-9]+$")
    title: Optional[str] = Field(default=None, max_length=256)
    layout: LayoutConfig = Field(default_factory=LayoutConfig)
    style: StyleConfig = Field(default_factory=StyleConfig)
    nodes: list[NodeSpec] = Field(min_length=0)
    edges: list[EdgeSpec] = Field(default_factory=list)
    groups: list[GroupSpec] = Field(default_factory=list)
    options: DiagramOptions = Field(default_factory=DiagramOptions)
    metadata: dict[str, Any] = Field(default_factory=dict)
