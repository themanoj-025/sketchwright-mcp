| Field | Value |
|---|---|
| Version | v1.0.0 |
| Last Updated | 2026-10-24 |
| Owner | Principal Product Architect |
| Status | Approved |

# 📄 Product Requirements Document (PRD) — Sketchwright

## 1. Executive Summary
Sketchwright is a zero-network, mathematically deterministic layout engine, CLI tool, and Model Context Protocol (MCP) server that transforms structured graph definitions and text DSLs into official Excalidraw scenes (`.excalidraw`) and standalone vector graphics (`.svg`). Tailored specifically for AI coding agents and automated developer tooling, it eliminates chaotic element overlaps, manual canvas positioning, and malformed JSON schemas. By enforcing Sugiyama layered heuristics, geometric edge routing, and reciprocal container-text bindings, Sketchwright provides software engineers and autonomous agents with an instant, production-grade diagramming interface.

## 2. Problem Statement
- **User Pain**: LLMs attempting to generate raw Excalidraw JSON routinely fail at geometric layout, placing nodes with overlapping coordinates, routing collinear edges that obscure labels, and generating unlinked or orphan text elements that float outside their bounding containers.
- **Evidence & Context**: Excalidraw scenes require exact reciprocal ID bindings (`boundElements`, `containerId`), strict coordinate transforms, and explicit font width estimations. Without a deterministic engine, AI agents produce unreadable diagrams that require tedious human canvas rearrangement.
- **Cost of Inaction**: Developers waste 15–30 minutes per diagram manually dragging shapes, or abandon visual architecture documentation altogether, increasing system design ambiguity across engineering teams.

## 3. Goals & Non-Goals

### 3.1 Core Goals
| Goal ID | Goal | Metric | Target |
|---|---|---|---|
| `G-001` | Mathematical Layout Determinism | Repeated layouts of identical graph inputs produce bit-for-bit identical coordinates | 100.0% |
| `G-002` | Zero Overlap Guarantee | Layout pass rate with zero overlapping nodes across DAG and cyclic inputs | > 99.9% |
| `G-003` | Low-Latency Execution | p95 execution latency for graphs with up to 100 nodes | < 250ms |
| `G-004` | Agent Stdio Integration | Valid MCP JSON-RPC stdio protocol compliance across all supported clients | 100.0% |

### 3.2 Non-Goals (v1 Scope Boundaries)
- **NG-01**: Interactive web canvas, graphical drag-and-drop editor, or browser-based GUI.
- **NG-02**: Raster image rendering (PNG, JPEG, WebP) requiring headless browser runtimes (Chromium/Puppeteer).
- **NG-03**: Remote cloud storage, multi-tenant databases, or team collaboration backends.
- **NG-04**: Arbitrary freehand drawing or artistic organic sketch generation.

## 4. Target Users & Personas

### Persona 1: "Agentic Arthur" — Autonomous AI Coding Agent
- **Role**: AI Coding Assistant (Claude Desktop, Cursor Agent, Windsurf Sidecar).
- **Context**: Autonomous software development workflows needing to visually map architecture before implementing code.
- **Goals**: Invoke programmatic tools over MCP stdio, pass JSON/DSL graphs, and receive validated file paths without syntax errors.
- **Frustrations**: Canvas coordinates that require visual inspection; tools that dump diagnostic logs to `stdout` corrupting JSON-RPC frames.
- **Quote**: *"I need a deterministic tool that converts my architectural thoughts into an Excalidraw file without me calculating pixel geometry."*
- **Technical Comfort**: Machine (Structured JSON-RPC protocol).

### Persona 2: "Staff Engineer Sarah" — Systems Architect
- **Role**: Staff Infrastructure / Backend Architect.
- **Context**: Designs microservice ecosystems, data pipelines, and infrastructure topologies in markdown documentation.
- **Goals**: Write concise text DSLs or structured YAML/JSON in Git repos and compile them to version-controlled diagrams.
- **Frustrations**: Heavy GUI tools that cannot be automated in CI/CD pipelines; proprietary diagram formats that resist Git diffing.
- **Quote**: *"I want diagram-as-code with real Excalidraw hand-drawn aesthetics, verifiable in automated CI builds."*
- **Technical Comfort**: Expert (CLI, Python, Git).

## 5. User Stories
| ID | As a... | I want to... | So that... | Priority | Acceptance Criteria |
|---|---|---|---|:---:|---|
| `US-001` | AI Coding Agent | Call `sketchwright_generate` with a graph JSON over MCP | I can generate an Excalidraw diagram for the user | **P0** | Returns valid scene file path; exits cleanly; zero logs on `stdout`. |
| `US-002` | Software Engineer | Run `sketchwright generate input.json -o out.svg` via CLI | I can embed standalone vector graphics in README files | **P0** | Produces valid XML SVG without external web dependencies. |
| `US-003` | Systems Designer | Write a compact line-based text DSL | I can quickly sketch nodes and connections without writing raw JSON | **P1** | Supports node definitions, labeled arrows (`-->`), and layout hints. |
| `US-004` | Developer | Run `sketchwright validate diagram.excalidraw` | I can ensure the scene conforms to Excalidraw v2 element schema | **P0** | Identifies broken bindings, negative dimensions, and malformed IDs. |
| `US-005` | AI Coding Agent | Call `sketchwright_update` with patch operations | I can add or modify nodes in an existing diagram without regenerating | **P1** | Preserves unmodified node coordinates and visual styling. |

## 6. Feature List

```mermaid
quadrantChart
    title Feature Prioritization (Impact vs Effort)
    x-axis Low Effort --> High Effort
    y-axis Low Impact --> High Impact
    quadrant-1 High Impact / High Effort (Strategic)
    quadrant-2 High Impact / Low Effort (Quick Wins)
    quadrant-3 Low Impact / Low Effort (Fill-ins)
    quadrant-4 Low Impact / High Effort (Reconsider)
    "REQ-001 Deterministic Sugiyama Layout": [0.65, 0.95]
    "REQ-002 FastMCP Stdio Server": [0.35, 0.90]
    "REQ-003 Standalone SVG Export": [0.40, 0.85]
    "REQ-004 Text DSL Parser": [0.30, 0.75]
    "REQ-005 Excalidraw v2 Validator": [0.25, 0.80]
    "REQ-006 Visual Frame Grouping": [0.55, 0.70]
    "REQ-007 Incremental Diagram Patching": [0.75, 0.65]
```

### Epic 1: Core Layout Engine & Geometry
- `REQ-001`: **Sugiyama Layered Layout** — Multi-pass hierarchical layout algorithm with cycle-breaking DFS, longest-path ranking, and barycentric crossing reduction. (*P0 — Status: Approved*)
- `REQ-002`: **Alternative Algorithms** — Deterministic `grid` and hierarchical `tree` layouts with configurable node and rank spacing. (*P1 — Status: Approved*)
- `REQ-003`: **Orthogonal Edge Routing** — Stepped polyline edge path generation with obstacle clearance and label offset calculations. (*P0 — Status: Approved*)

### Epic 2: Excalidraw Scene Serialization & Validation
- `REQ-004`: **Element Schema Compliance** — Generation of official Excalidraw v2 element structures (`rectangle`, `ellipse`, `diamond`, `cylinder`, `arrow`, `text`, `frame`). (*P0 — Status: Approved*)
- `REQ-005`: **Container-Text Auto-Wrapping** — Calculation of approximate font metrics to dynamically wrap labels and compute container dimensions. (*P0 — Status: Approved*)
- `REQ-006`: **Reciprocal Binding Generation** — Creation of deterministic element IDs via salted SHA-256 with bi-directional `boundElements` references. (*P0 — Status: Approved*)
- `REQ-007`: **Offline SVG Export** — Pure-Python vector graphics rendering with rough-style styling and embedded text. (*P0 — Status: Approved*)
- `REQ-008`: **Scene Validator** — Structural schema validation detecting orphan bindings, missing properties, or non-finite coordinates. (*P0 — Status: Approved*)

### Epic 3: Protocol & Interfaces
- `REQ-009`: **Model Context Protocol (MCP) Server** — FastMCP implementation exposing 6 tools, 3 resources, and 3 prompts over stdio with strict stderr diagnostic logging. (*P0 — Status: Approved*)
- `REQ-010`: **Unified CLI Interface** — Console commands (`generate`, `layout`, `validate`, `capabilities`, `mcp`) with standard POSIX exit codes and help screens. (*P0 — Status: Approved*)
- `REQ-011`: **DSL & Structured Parsers** — Ingestion of structured JSON and line-based shorthand diagram text specifications. (*P1 — Status: Approved*)

## 7. High-Level User Journeys

```mermaid
flowchart TD
    Start([User / AI Agent]) --> Decision{Input Format?}
    Decision -- JSON Spec --> ParseJSON[Structured Parser (structured.py)]
    Decision -- Text DSL --> ParseDSL[Text DSL Parser (text.py)]
    
    ParseJSON --> PydanticVal[Pydantic Validation (DiagramSpec)]
    ParseDSL --> PydanticVal
    
    PydanticVal --> LayoutEngine[Deterministic Layout Engine (algorithms.py)]
    LayoutEngine --> CycleBreak[Cycle Detection & Layer Assignment]
    CycleBreak --> Routing[Edge Stepped Routing & Label Clearance]
    
    Routing --> Serializer[Excalidraw Serializer (serializer.py)]
    Serializer --> BindingEngine[Salted SHA-256 Element & Binding Engine]
    
    BindingEngine --> Validator[Scene Schema Validator (validator.py)]
    Validator --> ExportChoice{Target Output?}
    
    ExportChoice -- .excalidraw --> WriteJSON[Atomic File Write (scene.excalidraw)]
    ExportChoice -- .svg --> RenderSVG[Vector SVG Renderer (scene.svg)]
    
    WriteJSON --> Complete([Process Success / MCP Tool Response])
    RenderSVG --> Complete
```

## 8. Success Metrics / KPIs
| Metric ID | Metric | Baseline | Target (6 Mo) | Measurement Method |
|---|---|---|---|---|
| `MET-001` | **Deterministic Reproducibility** | 100% | 100.0% | Hash comparison of consecutive layout runs |
| `MET-002` | **Layout Pass Rate (No Overlaps)** | 98.5% | > 99.9% | Automated bounding-box collision test suite |
| `MET-003` | **p95 Generation Latency** | 350ms | < 250ms | Benchmark test suite on 100-node random DAGs |
| `MET-004` | **MCP Protocol Conformance** | 100% | 100.0% | Official MCP inspector test suite execution |
| `MET-005` | **Security Invariant Enforcement** | 100% | 100.0% | Malicious payload test cases (path traversal, 1 MB DOS) |

## 9. Assumptions & Dependencies
- **ASM-001**: AI host environments provide Python >= 3.12 and shell/stdio process execution access.
- **ASM-002**: Host systems have write permissions in designated output directories or temporary scratch paths.
- **DEP-001**: `mcp >= 2.3.0` (Official Model Context Protocol SDK).
- **DEP-002**: `pydantic >= 2.14.0` (High-performance schema validation and serialization).

## 10. Top Risks Summary (see RiskRegister.md)
1. **RSK-001**: Output path traversal escapes outside intended project folders if unconfined (`SKETCHWRIGHT_ALLOWED_DIR` sandbox addresses this).
2. **RSK-002**: Large pathological cyclic graphs cause quadratic crossing minimization slowdowns (Cycle-breaking DFS & timeout limits mitigate this).
3. **RSK-003**: Inadvertent diagnostic logging to `stdout` corrupts MCP stdio JSON-RPC frames (Strict `stderr` redirect logging enforces this).

## 11. Release Criteria (v1.0.0 GA Checklist)
- [x] All 91 automated unit, integration, and contract tests pass with 100% success.
- [x] Strict static type-checking (`mypy --strict`) passes with 0 errors across all modules.
- [x] Code style and formatting (`ruff`) passes with 0 violations.
- [x] MCP tools verified against Claude Desktop and CLI subprocess clients.
- [x] Security limits (1 MB payload, 500 nodes, 1000 edges) actively enforced and verified.
- [x] Complete documentation suite published and cross-linked in `/docs/`.

## 12. Open Questions
| Question ID | Question | Owner | Resolve By | Current Lean |
|---|---|---|---|---|
| `QST-001` | Should text-based DSL support explicit port-to-port edge bindings? | Lead Eng | v1.1.0 | Current lean: keep edge routing heuristic-driven in v1. |
| `QST-002` | Add optional native Mermaid diagram import parser? | Product | v1.2.0 | Current lean: evaluate user demand post-v1 launch. |

## 13. Related Documents
| Document | Relationship & Cross-Reference |
|---|---|
| [TechSpec.md](file:///f:/GITHUB/sketchwright-mcp/docs/TechSpec.md) | Technical architecture, data flow diagrams, and component breakdown. |
| [AppFlow.md](file:///f:/GITHUB/sketchwright-mcp/docs/AppFlow.md) | Execution states, CLI option trees, and MCP request-response lifecycles. |
| [Design.md](file:///f:/GITHUB/sketchwright-mcp/docs/Design.md) | Excalidraw visual style tokens, stroke palettes, and font sizing rules. |
| [Schema.md](file:///f:/GITHUB/sketchwright-mcp/docs/Schema.md) | Pydantic data models and Excalidraw element JSON data structures. |
| [ImplementationPlan.md](file:///f:/GITHUB/sketchwright-mcp/docs/ImplementationPlan.md) | Phased task breakdown and engineering milestones. |
| [Tracker.md](file:///f:/GITHUB/sketchwright-mcp/docs/Tracker.md) | Real-time status dashboard and task completion progress. |
| [Rules.md](file:///f:/GITHUB/sketchwright-mcp/docs/Rules.md) | Coding standards, Git conventions, and AI agent operating instructions. |
| [API.md](file:///f:/GITHUB/sketchwright-mcp/docs/API.md) | Detailed MCP tool schemas, CLI flags, and Python facade APIs. |
| [SecurityAndCompliance.md](file:///f:/GITHUB/sketchwright-mcp/docs/SecurityAndCompliance.md) | Threat model, sandbox confinements, and input limit defenses. |
| [Testing.md](file:///f:/GITHUB/sketchwright-mcp/docs/Testing.md) | Test pyramid, determinism test strategies, and coverage goals. |
| [Deployment.md](file:///f:/GITHUB/sketchwright-mcp/docs/Deployment.md) | Package distribution, PyPI release workflows, and CI validation. |
| [Glossary.md](file:///f:/GITHUB/sketchwright-mcp/docs/Glossary.md) | Canonical domain definitions and terminology dictionary. |
| [RiskRegister.md](file:///f:/GITHUB/sketchwright-mcp/docs/RiskRegister.md) | Exhaustive failure mode analysis, mitigations, and owner assignments. |
