# Changelog

All notable changes to Sketchwright will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-10-23

### Added
- Canonical diagram specification schema v1.0 (`DiagramSpec`, `NodeSpec`, `EdgeSpec`, `LayoutConfig`, `StyleConfig`).
- Deterministic Sugiyama-style layered layout engine supporting cycles, disconnected components, and multi-directional flows (`LR`, `RL`, `TB`, `BT`).
- Excalidraw v2 scene serializer with reciprocal arrow bindings and centered text container bindings.
- Scene validator verifying structural invariants, finite geometry, and binding integrity.
- Standalone valid SVG export with proper XML namespaces and arrowhead markers.
- Model Context Protocol (MCP 2.3.0) integration exposing 5 tools, 2 resources, and 2 prompts.
- Strict stdio discipline ensuring logs never corrupt protocol framing on `stdout`.
- Command-line interface with `validate`, `generate`, `layout`, `capabilities`, and `mcp` subcommands.
- Comprehensive test suite covering unit, integration, contract, and e2e subprocess tests (56 tests passing).
- Cross-platform GitHub Actions continuous integration workflow.
- Complete documentation including installation, architecture, MCP setup, security, and troubleshooting.
