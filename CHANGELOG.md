# Changelog

All notable changes to Sketchwright will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-10-23

### Added
- Canonical diagram specification schema v1.0 (`DiagramSpec`, `NodeSpec`, `EdgeSpec`, `GroupSpec`, `LayoutConfig`, `StyleConfig`).
- Deterministic Sugiyama-style layered layout engine supporting cycles, disconnected components, and multi-directional flows (`LR`, `RL`, `TB`, `BT`).
- Excalidraw v2 scene serializer with reciprocal arrow bindings, centered text container bindings, and dashed visual group boundaries.
- Incremental diagram update engine (`update_diagram_spec` and `sketchwright_update_diagram`) with stable-ID matching, unambiguous label fallback, and cascading edge pruning.
- Scene validator verifying structural invariants, finite geometry, reciprocal bindings, and visual element overlap diagnostics.
- Standalone valid SVG export with multiline `<tspan>` formatting, XML escaping, and arrowhead markers.
- Model Context Protocol (MCP 2.3.0) integration exposing 6 tools, 3 resources, and 3 prompts.
- Strict stdio discipline ensuring logs never corrupt protocol framing on `stdout`.
- Command-line interface with `validate`, `generate`, `layout`, `capabilities`, and `mcp` subcommands with documented exit codes (`0`, `1`, `2`).
- Filesystem security enforcement preventing directory traversal escaping authorized roots.
- Comprehensive test suite covering unit, property, integration, contract, and e2e subprocess tests.
- Cross-platform GitHub Actions continuous integration workflow on Linux and Windows.
- Complete documentation including architecture, installation, MCP integration, layout engine, security, troubleshooting, and testing guides.

