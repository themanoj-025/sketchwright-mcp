# Sketchwright Documentation Suite

Welcome to the **Sketchwright** documentation suite. Sketchwright is an authoritative, deterministic layout engine and Model Context Protocol (MCP) server that converts unstructured, natural-language diagram requests into aesthetically balanced, production-grade Excalidraw visual artifacts and standalone SVG files.

---

## 📁 Documentation Architecture & Directory Map

The documentation is organized into four core functional domains:

```text
docs/
├── README.md                      # Documentation suite index & reading guide (this document)
├── product/                       # Product requirements, domain models & user flows
│   ├── PRD.md                     # Product Requirements Document & core value propositions
│   ├── AppFlow.md                 # Execution states, CLI trees & MCP protocol lifecycles
│   └── Glossary.md                # Canonical terminology & domain dictionary
├── architecture/                  # Deep technical specifications, design & schemas
│   ├── TechSpec.md                # C4 architecture, Sugiyama pipeline & performance bounds
│   ├── Design.md                  # Excalidraw visual style tokens & typographic rules
│   ├── Schema.md                  # Canonical JSON/Text DSL data models & Pydantic schemas
│   ├── API.md                     # FastMCP tool signatures & CLI parameter references
│   └── decisions/                 # Architecture Decision Records (ADRs)
│       ├── 0001-mcp-v2-sdk.md     # ADR 0001: Model Context Protocol Python SDK adoption
│       ├── 0002-deterministic-layout.md # ADR 0002: Native deterministic layout engine
│       └── 0003-pypi-naming-and-updates.md # ADR 0003: PyPI namespace & delta updates
├── guides/                        # Operational runbooks, configurations & user handbooks
│   ├── configuration.md           # Environment variables, defaults & tuning limits
│   ├── Deployment.md              # Build, release, PyPI distribution & host configs
│   ├── troubleshooting.md         # Diagnostic procedures, error codes & resolutions
│   └── SecurityAndCompliance.md   # Threat model, sandboxing & payload limits
└── development/                   # Engineering standards, testing & quality requirements
    ├── Rules.md                   # Engineering standards, coding guidelines & invariants
    └── testing.md                 # Test strategy, critical test cases & verification gates
```

---

## 🗺️ Master Documentation Directory

### 1. Product & Domain (`docs/product/`)
Focused on what we are building, why it exists, and the user journeys it enables:

| Document | Primary Audience | Key Contents & Verification Objectives |
|---|---|---|
| [**PRD.md**](file:///f:/GITHUB/sketchwright-mcp/docs/product/PRD.md) | Product Managers, Architects | Core problem statement, personas, functional requirements (`REQ-001`–`REQ-007`), performance metrics, and acceptance criteria. |
| [**AppFlow.md**](file:///f:/GITHUB/sketchwright-mcp/docs/product/AppFlow.md) | Frontend/Backend Eng, Designers | CLI option state trees, stdio MCP lifecycle state machines, error transition handling, and client integration flows. |
| [**Glossary.md**](file:///f:/GITHUB/sketchwright-mcp/docs/product/Glossary.md) | All Contributors & Developers | Canonical definitions for graph layout terms (Sugiyama, barycentric heuristic, cycle breaking) and Excalidraw primitives. |

---

### 2. Architecture & Specifications (`docs/architecture/`)
Deep-dive technical blueprints and formal data contracts:

| Document | Primary Audience | Key Contents & Verification Objectives |
|---|---|---|
| [**TechSpec.md**](file:///f:/GITHUB/sketchwright-mcp/docs/architecture/TechSpec.md) | Senior Engineers, Reviewers | 4-phase Sugiyama layout pipeline, collision detection geometry, C4 system architecture diagrams, and resource limits. |
| [**Design.md**](file:///f:/GITHUB/sketchwright-mcp/docs/architecture/Design.md) | UI/UX Engineers, Developers | Excalidraw visual style tokens, stroke and fill color palettes, proportional typography metrics, and connector arrow routing. |
| [**Schema.md**](file:///f:/GITHUB/sketchwright-mcp/docs/architecture/Schema.md) | Integration Engineers, Tool Users | Canonical Pydantic schemas, JSON schema specifications, Text DSL shorthand grammar, and Excalidraw scene JSON formats. |
| [**API.md**](file:///f:/GITHUB/sketchwright-mcp/docs/architecture/API.md) | Client Integrators, Developers | FastMCP tool signatures (`sketchwright_generate`, `sketchwright_validate`, etc.), CLI flags, and Python facade APIs. |
| [**decisions/**](file:///f:/GITHUB/sketchwright-mcp/docs/architecture/decisions) | System Architects | Historical Architecture Decision Records (ADRs) capturing key architectural pivots and technology choices. |

---

### 3. Guides & Operations (`docs/guides/`)
Runbooks for installation, configuration, security hardening, and deployment:

| Document | Primary Audience | Key Contents & Verification Objectives |
|---|---|---|
| [**configuration.md**](file:///f:/GITHUB/sketchwright-mcp/docs/guides/configuration.md) | DevOps, System Operators | Environment variables (`SKETCHWRIGHT_DETERMINISTIC`, `SKETCHWRIGHT_LOG_LEVEL`), timeouts, and default dimensions. |
| [**Deployment.md**](file:///f:/GITHUB/sketchwright-mcp/docs/guides/Deployment.md) | Release Engineers | Packaging commands with `uv build`, PyPI release workflows, client config snippets for MCP hosts. |
| [**troubleshooting.md**](file:///f:/GITHUB/sketchwright-mcp/docs/guides/troubleshooting.md) | Support, Developers | Step-by-step diagnostic workflows, common error codes (`400`, `413`, `500`), and logging inspection steps. |
| [**SecurityAndCompliance.md**](file:///f:/GITHUB/sketchwright-mcp/docs/guides/SecurityAndCompliance.md) | Security Auditors | STRIDE threat analysis, filesystem sandbox confinements, payload limits (1 MB ceiling), and CVE mitigation strategies. |

---

### 4. Development & Engineering (`docs/development/`)
Engineering operational standards, testing pyramids, and quality gates:

| Document | Primary Audience | Key Contents & Verification Objectives |
|---|---|---|
| [**Rules.md**](file:///f:/GITHUB/sketchwright-mcp/docs/development/Rules.md) | Contributors & Maintainers | Repository coding conventions, Git branching & commit standards (`RULE-001`–`RULE-010`), and architectural invariants. |
| [**testing.md**](file:///f:/GITHUB/sketchwright-mcp/docs/development/testing.md) | QA, Test Engineers | Test pyramid breakdown (Unit, Integration, Contract, E2E), critical test matrix (`TC-001`–`TC-010`), and coverage benchmarks. |

---

## ⚡ Recommended Reading Paths

- **If you are integrating Sketchwright with an MCP Client:**
  1. Start with [Deployment.md](file:///f:/GITHUB/sketchwright-mcp/docs/guides/Deployment.md#client-integration) for configuration snippets.
  2. Consult [API.md](file:///f:/GITHUB/sketchwright-mcp/docs/architecture/API.md) to inspect available tool parameters and options.
  3. Reference [Schema.md](file:///f:/GITHUB/sketchwright-mcp/docs/architecture/Schema.md) for custom JSON and text DSL examples.

- **If you are contributing to the layout algorithm or exporter:**
  1. Read [Rules.md](file:///f:/GITHUB/sketchwright-mcp/docs/development/Rules.md) for repository standards and pre-commit checks.
  2. Study [TechSpec.md](file:///f:/GITHUB/sketchwright-mcp/docs/architecture/TechSpec.md) for the 4-phase Sugiyama pipeline implementation.
  3. Review [testing.md](file:///f:/GITHUB/sketchwright-mcp/docs/development/testing.md) to execute unit and regression suites.

- **If you are troubleshooting an unexpected diagram layout:**
  1. Check [troubleshooting.md](file:///f:/GITHUB/sketchwright-mcp/docs/guides/troubleshooting.md) for common diagram rendering and layout issues.
  2. Review [configuration.md](file:///f:/GITHUB/sketchwright-mcp/docs/guides/configuration.md) to adjust node padding or spacing multipliers.
