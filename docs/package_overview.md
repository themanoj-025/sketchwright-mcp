# Package Overview: `sketchwright`

| Subpackage | Primary Responsibility | Key Files |
|---|---|---|
| `sketchwright.cli` | Command-line dispatch & help screens | `cli.py` |
| `sketchwright.config` | Settings & Limits dataclasses | `config.py` |
| `sketchwright.engine` | High-level pipeline coordinator | `generator.py`, `updater.py` |
| `sketchwright.excalidraw` | Excalidraw serialization & SVG export | `serializer.py`, `validator.py`, `export.py` |
| `sketchwright.layout` | Sugiyama, tree, and grid layout engines | `algorithms.py`, `engine.py`, `routing.py` |
| `sketchwright.mcp` | Model Context Protocol stdio server | `server.py`, `tools.py` |
| `sketchwright.models` | Pydantic v2 schemas and validation | `diagram.py`, `elements.py`, `validation.py` |
| `sketchwright.parser` | JSON & DSL parsing | `structured.py`, `text.py` |
