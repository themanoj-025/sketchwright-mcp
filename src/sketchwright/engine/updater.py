"""Deterministic incremental diagram updater.

Provides predictable addition, modification, renaming, and removal of nodes
and edges while preserving existing coordinates, references, and invariants.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from sketchwright.errors import ValidationError
from sketchwright.models.diagram import DiagramSpec
from sketchwright.models.elements import EdgeSpec, GroupSpec, NodeSpec
from sketchwright.models.validation import validate_diagram_spec


class DiagramUpdatePatch(BaseModel):
    """Specification of incremental updates to apply to a DiagramSpec."""

    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = None
    layout_overrides: Optional[dict[str, Any]] = None
    style_overrides: Optional[dict[str, Any]] = None
    add_nodes: list[NodeSpec] = Field(default_factory=list)
    update_nodes: list[dict[str, Any]] = Field(default_factory=list)
    remove_nodes: list[str] = Field(default_factory=list)  # IDs or unique labels
    add_edges: list[EdgeSpec] = Field(default_factory=list)
    remove_edges: list[str] = Field(default_factory=list)  # Edge IDs
    add_groups: list[GroupSpec] = Field(default_factory=list)


def update_diagram_spec(
    base: DiagramSpec,
    patch: DiagramUpdatePatch | dict[str, Any],
) -> DiagramSpec:
    """Apply an incremental update patch to an existing DiagramSpec.

    Rules (Section 8.1):
    1. Match nodes preferentially by stable ID.
    2. Fall back to label matching only if unambiguous. If multiple nodes share
       the target label, raise ValidationError.
    3. Never silently merge two distinct nodes.
    4. Removing a node cascades to automatically prune dangling edges.
    5. Preserves all unmentioned elements, styles, and options.
    6. Revalidates bindings and diagram invariants after mutation.
    """
    if isinstance(patch, dict):
        patch_obj = DiagramUpdatePatch.model_validate(patch)
    else:
        patch_obj = patch

    # Clone base structures
    nodes_by_id: dict[str, NodeSpec] = {n.id: n.model_copy(deep=True) for n in base.nodes}
    edges_by_id: dict[str, EdgeSpec] = {e.id: e.model_copy(deep=True) for e in base.edges}
    groups_by_id: dict[str, GroupSpec] = {g.id: g.model_copy(deep=True) for g in base.groups}

    def _resolve_node_id(identifier: str) -> str:
        """Resolve an identifier to a node ID via exact ID match or unambiguous label."""
        if identifier in nodes_by_id:
            return identifier

        # Fallback to label matching
        matching = [nid for nid, n in nodes_by_id.items() if n.label == identifier]
        if len(matching) == 1:
            return matching[0]
        if len(matching) > 1:
            raise ValidationError(
                f"Ambiguous node reference '{identifier}': matches multiple nodes with IDs {matching}."
            )
        raise ValidationError(f"Node identifier '{identifier}' not found in diagram.")

    # 1. Update diagram metadata / title
    new_title = patch_obj.title if patch_obj.title is not None else base.title

    # 2. Add groups
    for g in patch_obj.add_groups:
        groups_by_id[g.id] = g.model_copy(deep=True)

    # 3. Add new nodes
    for n in patch_obj.add_nodes:
        if n.id in nodes_by_id:
            raise ValidationError(f"Cannot add node: ID '{n.id}' already exists in diagram.")
        nodes_by_id[n.id] = n.model_copy(deep=True)

    # 4. Update existing nodes (properties and optional renaming)
    for u in patch_obj.update_nodes:
        target_ref = u.get("id") or u.get("target") or u.get("label")
        if not target_ref:
            raise ValidationError("Node update item must specify 'id', 'target', or 'label'.")

        target_id = _resolve_node_id(str(target_ref))
        node = nodes_by_id[target_id]

        new_id = u.get("new_id")
        if new_id and new_id != target_id:
            if new_id in nodes_by_id:
                raise ValidationError(f"Cannot rename node to '{new_id}': ID already exists.")
            del nodes_by_id[target_id]
            node.id = new_id
            nodes_by_id[new_id] = node

            # Propagate renamed node ID to existing edges
            for e in edges_by_id.values():
                if e.source == target_id:
                    e.source = new_id
                if e.target == target_id:
                    e.target = new_id

        if "label" in u:
            node.label = str(u["label"])
        if "shape" in u:
            node.shape = u["shape"]
        if "group" in u:
            node.group = u["group"]
        if "metadata" in u and isinstance(u["metadata"], dict):
            node.metadata.update(u["metadata"])

    # 5. Remove nodes (and cascade delete connected edges)
    for r in patch_obj.remove_nodes:
        rem_id = _resolve_node_id(r)
        if rem_id in nodes_by_id:
            del nodes_by_id[rem_id]

        # Prune dangling edges connected to removed node
        edges_to_prune = [eid for eid, e in edges_by_id.items() if e.source == rem_id or e.target == rem_id]
        for eid in edges_to_prune:
            del edges_by_id[eid]

    # 6. Remove edges
    for e_rem in patch_obj.remove_edges:
        if e_rem in edges_by_id:
            del edges_by_id[e_rem]

    # 7. Add new edges
    for e_new in patch_obj.add_edges:
        if e_new.id in edges_by_id:
            raise ValidationError(f"Cannot add edge: ID '{e_new.id}' already exists in diagram.")
        edges_by_id[e_new.id] = e_new.model_copy(deep=True)

    # 8. Apply layout/style overrides if provided
    new_layout = base.layout.model_copy(deep=True)
    if patch_obj.layout_overrides:
        for k, v in patch_obj.layout_overrides.items():
            if hasattr(new_layout, k):
                setattr(new_layout, k, v)

    new_style = base.style.model_copy(deep=True)
    if patch_obj.style_overrides:
        for k, v in patch_obj.style_overrides.items():
            if hasattr(new_style, k):
                setattr(new_style, k, v)

    updated_spec = DiagramSpec(
        schema_version=base.schema_version,
        title=new_title,
        layout=new_layout,
        style=new_style,
        nodes=list(nodes_by_id.values()),
        edges=list(edges_by_id.values()),
        groups=list(groups_by_id.values()),
        options=base.options.model_copy(deep=True),
        metadata=dict(base.metadata),
    )

    # 9. Verify overall diagram invariants and binding integrity
    val_res = validate_diagram_spec(updated_spec)
    if not val_res.is_valid:
        raise ValidationError(f"Updated diagram failed validation: {'; '.join(val_res.errors)}")

    return updated_spec
