"""Unit tests for Excalidraw scene validator."""

from sketchwright.excalidraw.validator import validate_excalidraw_scene


def test_valid_minimal_scene() -> None:
    scene = {
        "type": "excalidraw",
        "version": 2,
        "source": "https://sketchwright.dev",
        "elements": [
            {
                "id": "elem1",
                "type": "rectangle",
                "x": 10.0,
                "y": 20.0,
                "width": 100.0,
                "height": 50.0,
            }
        ],
        "appState": {},
        "files": {},
    }
    res = validate_excalidraw_scene(scene)
    assert res.is_valid
    assert len(res.errors) == 0


def test_invalid_scene_type() -> None:
    scene = {
        "type": "not_excalidraw",
        "version": 2,
        "elements": [],
    }
    res = validate_excalidraw_scene(scene)
    assert not res.is_valid
    assert any("Invalid scene type" in err for err in res.errors)


def test_duplicate_element_id_detected() -> None:
    scene = {
        "type": "excalidraw",
        "version": 2,
        "elements": [
            {"id": "dup", "type": "rectangle", "x": 0, "y": 0, "width": 10, "height": 10},
            {"id": "dup", "type": "rectangle", "x": 20, "y": 20, "width": 10, "height": 10},
        ],
        "appState": {},
        "files": {},
    }
    res = validate_excalidraw_scene(scene)
    assert not res.is_valid
    assert any("Duplicate element id 'dup'" in err for err in res.errors)


def test_dangling_arrow_binding_detected() -> None:
    scene = {
        "type": "excalidraw",
        "version": 2,
        "elements": [
            {
                "id": "arrow1",
                "type": "arrow",
                "x": 0,
                "y": 0,
                "width": 100,
                "height": 100,
                "startBinding": {"elementId": "missing_node"},
            }
        ],
        "appState": {},
        "files": {},
    }
    res = validate_excalidraw_scene(scene)
    assert not res.is_valid
    assert any("dangling startBinding" in err for err in res.errors)


def test_nan_coordinates_rejected() -> None:
    scene = {
        "type": "excalidraw",
        "version": 2,
        "elements": [{"id": "e1", "type": "rectangle", "x": float("nan"), "y": 0, "width": 10, "height": 10}],
        "appState": {},
        "files": {},
    }
    res = validate_excalidraw_scene(scene)
    assert not res.is_valid
    assert any("invalid numeric x" in err for err in res.errors)
