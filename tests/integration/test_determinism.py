"""Integration tests for deterministic layout and byte-for-byte serialization reproducibility."""

import json

from sketchwright import generate_diagram


def test_reproducible_identical_outputs() -> None:
    spec = {
        "schema_version": "1.0",
        "title": "Deterministic Benchmark",
        "layout": {"algorithm": "layered", "direction": "LR"},
        "nodes": [
            {"id": "auth", "label": "Auth Service", "shape": "rounded_rectangle"},
            {"id": "orders", "label": "Orders Service", "shape": "rectangle"},
            {"id": "db", "label": "Database", "shape": "cylinder"},
        ],
        "edges": [
            {"id": "e1", "source": "auth", "target": "orders", "label": "token"},
            {"id": "e2", "source": "orders", "target": "db", "label": "persist"},
        ],
        "options": {"deterministic": True},
    }

    # Generate 3 separate runs
    run1 = generate_diagram(spec)
    run2 = generate_diagram(spec)
    run3 = generate_diagram(spec)

    json1 = json.dumps(run1.scene, sort_keys=True, indent=2)
    json2 = json.dumps(run2.scene, sort_keys=True, indent=2)
    json3 = json.dumps(run3.scene, sort_keys=True, indent=2)

    assert json1 == json2
    assert json2 == json3

    # Check element IDs match across runs
    ids1 = [e["id"] for e in run1.scene["elements"]]
    ids2 = [e["id"] for e in run2.scene["elements"]]
    assert ids1 == ids2
