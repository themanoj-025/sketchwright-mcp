"""Minimal runnable example demonstrating Sketchwright's public Python API."""

from sketchwright import generate_diagram

spec = {
    "schema_version": "1.0",
    "title": "Hello World Diagram",
    "layout": {"direction": "LR"},
    "nodes": [
        {"id": "a", "label": "Hello", "shape": "rectangle"},
        {"id": "b", "label": "World", "shape": "rounded_rectangle"},
    ],
    "edges": [{"id": "e1", "source": "a", "target": "b", "label": "greets"}],
}

if __name__ == "__main__":
    result = generate_diagram(spec, output_path="hello_world.excalidraw", overwrite=True)
    print("Diagram generated successfully!")
    print(f"Elements: {len(result.scene['elements'])}")
    print(f"Canvas size: {result.laid_out.canvas_rect.width} x {result.laid_out.canvas_rect.height}")
    print(f"Valid Excalidraw scene: {result.validation.is_valid}")
