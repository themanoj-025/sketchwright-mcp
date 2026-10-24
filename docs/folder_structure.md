# Repository Folder Structure

```
sketchwright-mcp/
├── .github/                   # CI/CD automation workflows, issue/PR templates, and dependabot configuration
├── docs/                      # Architectural specifications, MCP integration guides, and configuration docs
│   └── migration/             # Zero-regression restructuring protocol audit, ADRs, and verification reports
├── examples/                  # Client MCP configurations and sample architecture graph JSON files
├── src/
│   └── sketchwright/          # Core Python package root
│       ├── engine/            # High-level diagram generation, update, and pipeline orchestration
│       ├── excalidraw/        # Excalidraw JSON element serialization, schema validation, and SVG export
│       ├── layout/            # Deterministic geometric layout algorithms (Sugiyama layered, grid, tree)
│       ├── mcp/               # Model Context Protocol (MCP) FastMCP stdio server and tool definitions
│       ├── models/            # Pydantic v2 diagram schema, node/edge models, and layout metadata
│       └── parser/            # Structured JSON and human-readable text DSL input parsers
├── tests/
│   ├── contract/              # MCP protocol interface schema and contract test suite
│   ├── e2e/                   # Live subprocess MCP stdio client-server integration tests
│   ├── fixtures/              # Reusable valid/invalid graph JSON fixtures (cyclic, unicode, dangling)
│   ├── integration/           # Multi-component pipeline and geometric determinism tests
│   └── unit/                  # Fast component unit tests covering layout, models, CLI, and serializer
├── CHANGELOG.md               # Chronological release notes and version history
├── CONTRIBUTING.md            # Contributor guidelines and environment setup instructions
├── LICENSE                    # MIT license declaration
├── PROJECT_OVERVIEW.md        # Comprehensive enterprise architectural specification
├── pyproject.toml             # Build packaging manifest (Python >=3.12, uv_build backend)
├── README.md                  # Project overview, badges, quickstart, and CLI/MCP documentation
├── SECURITY.md                # Vulnerability disclosure and reporting policies
└── uv.lock                    # Cryptographic dependency lockfile
```
