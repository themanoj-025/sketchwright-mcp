"""Unit tests for JSON and text DSL parsers."""

from pathlib import Path

import pytest

from sketchwright.config import Limits
from sketchwright.errors import FileSystemError, ValidationError
from sketchwright.parser.structured import parse_json_file, parse_json_string
from sketchwright.parser.text import parse_text_dsl


def test_parse_valid_json_string() -> None:
    raw = '{"schema_version": "1.0", "nodes": [{"id": "x", "label": "X"}]}'
    spec = parse_json_string(raw)
    assert len(spec.nodes) == 1
    assert spec.nodes[0].id == "x"


def test_parse_json_exceeds_byte_limit() -> None:
    limits = Limits(max_input_bytes=20)
    raw = '{"schema_version": "1.0", "nodes": []}'
    with pytest.raises(ValidationError) as exc:
        parse_json_string(raw, limits=limits)
    assert "exceeds maximum limit" in str(exc.value)


def test_parse_malformed_json_syntax() -> None:
    raw = '{"nodes": [}'
    with pytest.raises(ValidationError) as exc:
        parse_json_string(raw)
    assert "Invalid JSON syntax" in str(exc.value)


def test_parse_json_non_object_root() -> None:
    raw = '["not", "an", "object"]'
    with pytest.raises(ValidationError) as exc:
        parse_json_string(raw)
    assert "must be a JSON object" in str(exc.value)


def test_parse_text_dsl_pipeline() -> None:
    dsl = """
    title: Simple Flow
    direction: TB
    [start: ellipse: Start Here]
    [step1: rectangle: Process Work]
    [db: cylinder: Primary DB]

    start -> step1: begin
    step1 -> db: save
    """
    spec = parse_text_dsl(dsl)
    assert spec.title == "Simple Flow"
    assert spec.layout.direction == "TB"
    assert len(spec.nodes) == 3
    assert len(spec.edges) == 2
    assert spec.nodes[0].shape == "ellipse"
    assert spec.nodes[2].shape == "cylinder"


def test_parse_text_dsl_syntax_error() -> None:
    dsl = "invalid text that is not a node or edge"
    with pytest.raises(ValidationError) as exc:
        parse_text_dsl(dsl)
    assert "Unrecognized DSL syntax" in str(exc.value)


def test_parse_missing_file_raises_filesystem_error(tmp_path: Path) -> None:
    missing = tmp_path / "non_existent.json"
    with pytest.raises(FileSystemError):
        parse_json_file(missing)
