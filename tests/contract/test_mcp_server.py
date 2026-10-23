"""Contract tests verifying the MCP server tool discovery, invocation, resources, and prompts."""

import pytest

from sketchwright.mcp.server import create_server


@pytest.mark.asyncio
async def test_mcp_tools_discovery() -> None:
    server = create_server()
    tools = await server.list_tools()
    tool_names = {t.name for t in tools}

    expected_tools = {
        "sketchwright_create_diagram",
        "sketchwright_validate_diagram",
        "sketchwright_layout_diagram",
        "sketchwright_export_diagram",
        "sketchwright_get_capabilities",
    }
    assert expected_tools.issubset(tool_names)


@pytest.mark.asyncio
async def test_mcp_call_get_capabilities() -> None:
    server = create_server()
    result = await server.call_tool("sketchwright_get_capabilities", {})
    assert not result.is_error
    data = result.structured_content
    assert data is not None
    assert data["product"] == "Sketchwright"
    assert "rectangle" in data["supported_shapes"]


@pytest.mark.asyncio
async def test_mcp_call_create_diagram() -> None:
    server = create_server()
    spec = {
        "schema_version": "1.0",
        "title": "MCP Test Architecture",
        "nodes": [
            {"id": "client", "label": "Client App"},
            {"id": "server", "label": "Backend API"},
        ],
        "edges": [{"id": "e1", "source": "client", "target": "server", "label": "HTTP"}],
    }
    result = await server.call_tool("sketchwright_create_diagram", {"specification": spec})
    assert not result.is_error
    data = result.structured_content
    assert data is not None
    assert "scene" in data
    assert data["summary"]["valid"] is True
    assert data["summary"]["nodes_count"] == 2
    assert data["summary"]["edges_count"] == 1


@pytest.mark.asyncio
async def test_mcp_call_validate_diagram() -> None:
    server = create_server()
    spec = {
        "nodes": [{"id": "a"}, {"id": "b"}],
        "edges": [{"id": "e1", "source": "a", "target": "b"}],
    }
    result = await server.call_tool("sketchwright_validate_diagram", {"specification": spec})
    assert not result.is_error
    data = result.structured_content
    assert data["is_valid"] is True


@pytest.mark.asyncio
async def test_mcp_call_layout_diagram() -> None:
    server = create_server()
    spec = {
        "nodes": [{"id": "node1"}, {"id": "node2"}],
        "edges": [{"id": "e", "source": "node1", "target": "node2"}],
    }
    result = await server.call_tool("sketchwright_layout_diagram", {"specification": spec, "direction": "TB"})
    assert not result.is_error
    data = result.structured_content
    assert "node_positions" in data
    assert "routes" in data


@pytest.mark.asyncio
async def test_mcp_call_export_diagram() -> None:
    server = create_server()
    spec = {"nodes": [{"id": "x"}]}
    result = await server.call_tool(
        "sketchwright_export_diagram",
        {"specification": spec, "format": "svg"},
    )
    assert not result.is_error
    data = result.structured_content
    assert data["format"] == "svg"
    assert "<svg" in data["content_preview"]


@pytest.mark.asyncio
async def test_mcp_resources_and_prompts() -> None:
    server = create_server()
    resources = await server.list_resources()
    resource_uris = {r.uri for r in resources}
    assert "schema://v1.0" in resource_uris
    assert "capabilities://manifest" in resource_uris

    prompts = await server.list_prompts()
    prompt_names = {p.name for p in prompts}
    assert "architecture_diagram" in prompt_names
    assert "flowchart_diagram" in prompt_names
