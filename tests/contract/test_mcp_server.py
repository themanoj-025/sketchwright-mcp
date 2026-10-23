from pathlib import Path

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
async def test_mcp_call_update_diagram() -> None:
    server = create_server()
    base_spec = {
        "nodes": [{"id": "api", "label": "API Gateway"}],
        "edges": [],
    }
    patch = {
        "add_nodes": [{"id": "db", "label": "Database", "shape": "cylinder"}],
        "add_edges": [{"id": "e1", "source": "api", "target": "db"}],
    }
    result = await server.call_tool(
        "sketchwright_update_diagram",
        {"specification": base_spec, "patch": patch},
    )
    assert not result.is_error
    data = result.structured_content
    assert data["status"] == "success"
    assert "scene" in data
    assert data["summary"]["nodes_count"] == 2
    assert data["summary"]["edges_count"] == 1


@pytest.mark.asyncio
async def test_mcp_resources_and_prompts() -> None:
    server = create_server()
    resources = await server.list_resources()
    resource_uris = {r.uri for r in resources}
    assert "schema://v1.0" in resource_uris
    assert "capabilities://manifest" in resource_uris
    assert "guide://usage" in resource_uris

    prompts = await server.list_prompts()
    prompt_names = {p.name for p in prompts}
    assert "architecture_diagram" in prompt_names
    assert "flowchart_diagram" in prompt_names
    assert "dependency_graph" in prompt_names

    # Test reading guide resource
    guide_content = await server.read_resource("guide://usage")
    assert any("Sketchwright Usage Guide" in item.content for item in guide_content)

    # Test executing dependency_graph prompt
    dep_prompt = await server.get_prompt("dependency_graph", {"project_name": "Sketchwright"})
    assert "Sketchwright" in dep_prompt.messages[0].content.text


@pytest.mark.asyncio
async def test_mcp_call_invalid_input_error() -> None:
    from mcp.server.mcpserver.exceptions import ToolError

    server = create_server()
    # Malformed spec with unresolved endpoint
    bad_spec = {
        "nodes": [{"id": "a"}],
        "edges": [{"id": "e", "source": "a", "target": "non_existent"}],
    }
    with pytest.raises(ToolError) as exc:
        await server.call_tool("sketchwright_create_diagram", {"specification": bad_spec})
    assert "unresolved target endpoint 'non_existent'" in str(exc.value)


@pytest.mark.asyncio
async def test_mcp_call_path_traversal_blocked(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    from mcp.server.mcpserver.exceptions import ToolError

    server = create_server()
    safe_dir = tmp_path / "safe_dir"
    safe_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("SKETCHWRIGHT_ALLOWED_DIR", str(safe_dir))

    spec = {"nodes": [{"id": "n1"}]}
    bad_path = str(safe_dir / ".." / "escaped.excalidraw")

    with pytest.raises(ToolError) as exc:
        await server.call_tool(
            "sketchwright_create_diagram",
            {"specification": spec, "output_path": bad_path},
        )
    assert "resolves outside authorized directory" in str(exc.value)
