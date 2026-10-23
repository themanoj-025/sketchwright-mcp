"""Sketchwright Model Context Protocol (MCP) server implementation."""

from __future__ import annotations

import json
from typing import Any, Optional

from mcp.server.mcpserver import MCPServer

from sketchwright.logging_config import setup_logging
from sketchwright.mcp.tools import (
    handle_create_diagram,
    handle_export_diagram,
    handle_get_capabilities,
    handle_layout_diagram,
    handle_update_diagram,
    handle_validate_diagram,
)
from sketchwright.models.diagram import DiagramSpec


def create_server() -> MCPServer:
    """Create and configure the Sketchwright MCPServer with all tools, resources, and prompts."""
    server = MCPServer("sketchwright", version="0.1.0")

    # -------------------------------------------------------------
    # Tools Registration
    # -------------------------------------------------------------

    @server.tool(
        name="sketchwright_create_diagram",
        description="Generate an Excalidraw-compatible diagram scene JSON from a structured specification or DSL.",
    )
    def create_diagram(
        specification: Optional[dict[str, Any]] = None,
        text_dsl: Optional[str] = None,
        layout_overrides: Optional[dict[str, Any]] = None,
        output_path: Optional[str] = None,
        overwrite: bool = False,
    ) -> dict[str, Any]:
        return handle_create_diagram(
            specification=specification,
            text_dsl=text_dsl,
            layout_overrides=layout_overrides,
            output_path=output_path,
            overwrite=overwrite,
        )

    @server.tool(
        name="sketchwright_validate_diagram",
        description="Validate a diagram specification or an Excalidraw scene JSON for schema conformance and bindings.",
    )
    def validate_diagram(
        specification: Optional[dict[str, Any]] = None,
        scene: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        return handle_validate_diagram(
            specification=specification,
            scene=scene,
        )

    @server.tool(
        name="sketchwright_layout_diagram",
        description="Calculate deterministic node positions, bounding boxes, and edge routes for a diagram.",
    )
    def layout_diagram(
        specification: dict[str, Any],
        algorithm: Optional[str] = None,
        direction: Optional[str] = None,
    ) -> dict[str, Any]:
        return handle_layout_diagram(
            specification=specification,
            algorithm=algorithm,
            direction=direction,
        )

    @server.tool(
        name="sketchwright_export_diagram",
        description="Export a diagram specification or Excalidraw scene to .excalidraw JSON or standalone .svg.",
    )
    def export_diagram(
        specification: Optional[dict[str, Any]] = None,
        scene: Optional[dict[str, Any]] = None,
        format: str = "excalidraw",
        output_path: Optional[str] = None,
        overwrite: bool = False,
    ) -> dict[str, Any]:
        return handle_export_diagram(
            specification=specification,
            scene=scene,
            format=format,
            output_path=output_path,
            overwrite=overwrite,
        )

    @server.tool(
        name="sketchwright_update_diagram",
        description="Incrementally update an existing diagram specification (add/remove/rename nodes, add/remove edges) and regenerate scene.",
    )
    def update_diagram(
        specification: dict[str, Any],
        patch: dict[str, Any],
        generate_scene: bool = True,
        output_path: Optional[str] = None,
        overwrite: bool = False,
    ) -> dict[str, Any]:
        return handle_update_diagram(
            specification=specification,
            patch=patch,
            generate_scene=generate_scene,
            output_path=output_path,
            overwrite=overwrite,
        )

    @server.tool(
        name="sketchwright_get_capabilities",
        description="Discover Sketchwright's supported shapes, layout algorithms, directions, and resource limits.",
    )
    def get_capabilities() -> dict[str, Any]:
        return handle_get_capabilities()

    # -------------------------------------------------------------
    # Resources Registration
    # -------------------------------------------------------------

    @server.resource(
        "schema://v1.0",
        name="diagram_schema_v1",
        description="Canonical JSON schema definition for DiagramSpec v1.0.",
        mime_type="application/json",
    )
    def get_schema() -> str:
        schema = DiagramSpec.model_json_schema()
        return json.dumps(schema, indent=2)

    @server.resource(
        "capabilities://manifest",
        name="capability_manifest",
        description="Runtime capability manifest for Sketchwright.",
        mime_type="application/json",
    )
    def get_manifest() -> str:
        caps = handle_get_capabilities()
        return json.dumps(caps, indent=2)

    @server.resource(
        "guide://usage",
        name="usage_guide",
        description="Short usage guide and prompt engineering reference for Sketchwright.",
        mime_type="text/markdown",
    )
    def get_guide() -> str:
        return (
            "# Sketchwright Usage Guide for MCP AI Hosts\n\n"
            "## Recommended Workflow\n"
            "1. Call `sketchwright_get_capabilities` to inspect available shapes and limits.\n"
            "2. Formulate a structured specification matching `schema://v1.0` or lightweight DSL.\n"
            "3. Call `sketchwright_create_diagram` with your specification.\n"
            "4. For modifications to an existing diagram, call `sketchwright_update_diagram`.\n"
            "5. To export or convert to SVG, call `sketchwright_export_diagram`.\n\n"
            "## Supported Shapes\n"
            "- `rectangle`: Standard service, module, or component box\n"
            "- `rounded_rectangle`: Terminal node, queue, or consumer\n"
            "- `ellipse`: Event, process state, or start/stop\n"
            "- `diamond`: Decision or branching gateway\n"
            "- `cylinder`: Database, cache, disk, or data lake\n\n"
            "## Layout Directions\n"
            "- `LR`: Left-to-right (recommended for web architectures & pipelines)\n"
            "- `TB`: Top-to-bottom (recommended for flowcharts & hierarchies)\n"
            "- `RL`: Right-to-left\n"
            "- `BT`: Bottom-to-top\n"
        )

    # -------------------------------------------------------------
    # Prompts Registration
    # -------------------------------------------------------------

    @server.prompt(
        name="architecture_diagram",
        description="Prompt guidelines for requesting a software architecture diagram.",
    )
    def prompt_architecture(system_name: str = "System Architecture") -> str:
        return (
            f"Please generate a structured diagram specification for '{system_name}'.\n"
            "Include:\n"
            "- Client/browser nodes (shape: rectangle)\n"
            "- API gateway / microservices (shape: rectangle or rounded_rectangle)\n"
            "- Databases / storage (shape: cylinder)\n"
            "- Directed edges with protocol labels (e.g., HTTPS, gRPC, SQL)\n"
            "- Layout direction: 'LR' (left to right)\n"
        )

    @server.prompt(
        name="flowchart_diagram",
        description="Prompt guidelines for requesting a decision process or workflow flowchart.",
    )
    def prompt_flowchart(workflow_name: str = "Workflow Flowchart") -> str:
        return (
            f"Please generate a flowchart specification for '{workflow_name}'.\n"
            "Include:\n"
            "- Start/End terminal nodes (shape: rounded_rectangle or ellipse)\n"
            "- Process steps (shape: rectangle)\n"
            "- Decision branches (shape: diamond)\n"
            "- Directed edges with branch condition labels (e.g., Yes, No, Success, Error)\n"
            "- Layout direction: 'TB' (top to bottom)\n"
        )

    @server.prompt(
        name="dependency_graph",
        description="Prompt guidelines for requesting a software or package dependency graph.",
    )
    def prompt_dependency_graph(project_name: str = "Project Dependencies") -> str:
        return (
            f"Please generate a dependency graph specification for '{project_name}'.\n"
            "Include:\n"
            "- Root package/module nodes (shape: rectangle)\n"
            "- Intermediate and library dependencies (shape: rounded_rectangle)\n"
            "- Directed edges pointing from consumer to dependency (e.g., depends_on, imports)\n"
            "- Layout direction: 'TB' or 'LR'\n"
            "- Layout algorithm: 'layered'\n"
        )

    return server


def run_server(transport: str = "stdio") -> None:
    """Launch the MCP server with strict stdio discipline."""
    # Ensure all application logging is directed exclusively to stderr
    setup_logging(level="INFO", is_mcp=True)

    server = create_server()
    if transport == "stdio":
        server.run(transport="stdio")
    else:
        server.run(transport="stdio")
