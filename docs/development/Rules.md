| Field | Value |
|---|---|
| Version | v1.0.0 |
| Last Updated | 2026-10-24 |
| Owner | Principal Architect & Lead Maintainer |
| Status | Approved (Enforced) |

# 📄 Engineering Guidelines & Code Standards — Sketchwright

## 1. Guiding Principles

Every contributor working in this repository must uphold these non-negotiable principles:

1. **`RULE-001` Mathematical Determinism First**: Output coordinates, layout topology, and element IDs must be 100% reproducible. Given identical graph input, output JSON must match bit-for-bit.
2. **`RULE-002` Zero Network Access by Default**: Sketchwright is a local, offline computation engine. It must never initiate network connections, fetch external schemas at runtime, or make background telemetry calls.
3. **`RULE-003` Stdio Protocol Hygiene**: The standard output channel (`stdout`) is reserved strictly for valid JSON-RPC 2.0 frames when running under MCP mode, or intended CLI output data. All logging, diagnostics, warnings, and error stacks must be redirected to `stderr`.
4. **`RULE-004` Explicit Invariants Over Implicit Behavior**: Validate all inputs at the boundary using Pydantic. Reject malformed payloads immediately with descriptive diagnostics rather than silently coercing broken data.
5. **`RULE-005` Atomic, Reversible Commits**: Every change must represent a single logical unit of work. Keep PRs under 400 lines of diff. Never leave the main branch in an unbuildable or broken test state.
6. **`RULE-006` No Secret Ingestion**: Never hardcode credentials, private tokens, or sensitive machine paths. All configuration must resolve via standard flags or clean environment variables.

---

## 2. Code Style & Directory Architecture

### 2.1 Language & Tooling Standards
- **Python Version**: >= 3.12 exclusively.
- **Package Manager**: `uv` (Fast, reproducible dependency locking via `uv.lock`).
- **Linter & Formatter**: `ruff` with 120-character line lengths.
- **Type Checker**: `mypy --strict` with zero permitted untyped definitions in `src/`.
- **Testing Framework**: `pytest` with `pytest-asyncio` and `pytest-cov`.

### 2.2 Canonical Repository Structure

```text
sketchwright-mcp/
├── .github/                      # CI/CD workflows, issue templates, dependabot
│   └── workflows/
│       ├── ci.yml                # Lint, format, type-check, multi-OS test matrix
│       └── release.yml           # PyPI release automation
├── docs/                         # Documentation suite, specifications & runbooks
│   ├── README.md                 # Master index & reading paths
│   ├── product/                  # PRD, user journeys, app flows, and terminology glossary
│   ├── architecture/             # Technical specs, design tokens, schemas, APIs & ADRs
│   ├── guides/                   # Deployment, configuration, security, and troubleshooting
│   └── development/              # Engineering standards and test strategy
├── examples/                     # Sample input specs and MCP client configurations
├── src/                          # Canonical Python source tree (PEP 517/518)
│   └── sketchwright/
│       ├── __init__.py           # Package version and public exports
│       ├── cli.py                # Unified CLI entry point
│       ├── logging_config.py     # Stderr-only structured logging
│       ├── py.typed              # PEP 561 typing marker
│       ├── engine/               # Layout algorithms & geometry
│       ├── excalidraw/           # Excalidraw schema & serialization
│       ├── models/               # Abstract diagram specification models
│       ├── parser/               # Input format processors
│       └── mcp/                  # FastMCP stdio server and tools
└── tests/                        # Comprehensive automated test suite
    ├── conftest.py               # Shared pytest fixtures and sample graphs
    ├── contract/                 # MCP protocol interface schema and contract test suite
    ├── e2e/                      # Live subprocess MCP stdio client-server integration tests
    ├── fixtures/                 # Reusable valid/invalid graph JSON fixtures
    ├── integration/              # Multi-component pipeline and geometric determinism tests
    └── unit/                     # Fast component unit tests covering layout, models, CLI, and serializer
```

---

## 3. Git Workflow & Review Standards

```mermaid
flowchart LR
    Feature[feat/fix branch] --> PR[Create Pull Request]
    PR --> CI{CI Gates Pass?}
    CI -- No --> Fix[Fix Lint/Type/Tests]
    Fix --> PR
    CI -- Yes --> Review{Code Review & DoD}
    Review -- Approved --> Squash[Squash & Merge to main]
    Squash --> Tag[SemVer Tag & Publish]
```

### 3.1 Branching & Commit Conventions
- **Branch Naming**:
  - Features: `feat/<issue-id>-short-description`
  - Fixes: `fix/<issue-id>-short-description`
  - Chores / Docs: `chore/<description>` or `docs/<description>`
- **Commit Messages**: Enforce [Conventional Commits](https://www.conventionalcommits.org/):
  - `feat: add orthogonal stepped edge router for cyclic graphs`
  - `fix: prevent container text overflow on multi-line labels`
  - `docs: update Schema.md entity tables with group constraints`
  - `test: add fuzz tests for 1MB JSON input payloads`

### 3.2 Pull Request Criteria
- Maximum lines of diff: **400 LOC** (excluding generated lockfiles or test assets).
- 100% CI checks passing (Ruff, Mypy strict, multi-OS pytest).
- No force-pushes to `main`. All merges squashed with clean commit history.

---

## 4. Testing & Quality Requirements

- **`RULE-007` Coverage Threshold**: Maintain repository test coverage above **90%** at all times.
- **`RULE-008` Deterministic Regression Tests**: Any change affecting `engine/` or `excalidraw/` must include a test asserting bit-for-bit output reproducibility across consecutive runs.
- **`RULE-009` Collision Verification**: Every new layout feature must pass the automated bounding-box collision detection suite ensuring zero overlapping nodes.
- **`RULE-010` Stdio Leak Detection**: MCP unit tests must capture and assert that `sys.stdout` receives zero unformatted log statements during tool execution.

---

## 5. Security Baseline Rules

- **Input Size Ceilings**: JSON and DSL inputs parsed via CLI or MCP are capped at **1 MB** (1,048,576 bytes) to defend against memory exhaustion and regex ReDoS attacks.
- **Graph Complexity Limits**: Layout engine rejects input specifications exceeding **500 nodes** or **1,000 edges** per diagram.
- **Path Traversal Defense**: All output file writing must sanitize target paths using `os.path.realpath`, verifying that destination directories are writable and within intended scratch/target workspaces.
- **Dependency Sandboxing**: Run zero unpinned dependencies; lockfiles must be audited via automated security scanning (`dependabot.yml`).

---

## 6. Prohibited Anti-Patterns

| Anti-Pattern ID | Prohibited Pattern | Reason / Consequence |
|---|---|---|
| `ANTI-001` | Raw `print()` to `stdout` in core library | Corrupts JSON-RPC 2.0 framing, causing MCP host clients to disconnect |
| `ANTI-002` | Unseeded or non-deterministic random IDs (`uuid.uuid4()`) | Breaks diagram determinism; causes massive unnecessary Git diffs |
| `ANTI-003` | Importing external HTTP libraries (`requests`, `httpx`) | Violates zero-network architectural invariant (`RULE-002`) |
| `ANTI-004` | Hardcoded absolute paths in test fixtures | Breaks CI matrix runs on Windows, Linux, and macOS runners |
| `ANTI-005` | Floating text elements without container bindings | Causes unlinked labels to detach when diagrams are manipulated in Excalidraw |

---

## 7. Related Documents

| Document | Relationship & Cross-Reference |
|---|---|
| [PRD.md](file:///f:/GITHUB/sketchwright-mcp/docs/product/PRD.md) | Defines system goals (`G-###`) and user stories (`US-###`) enforced by these rules. |
| [TechSpec.md](file:///f:/GITHUB/sketchwright-mcp/docs/architecture/TechSpec.md) | Documents architectural boundaries and module contracts governed by these standards. |
| [AppFlow.md](file:///f:/GITHUB/sketchwright-mcp/docs/product/AppFlow.md) | Specifies execution states and error diagnostics enforced in Section 1. |
| [Design.md](file:///f:/GITHUB/sketchwright-mcp/docs/architecture/Design.md) | Enforces visual styling tokens and accessibility standards for generated elements. |
| [Schema.md](file:///f:/GITHUB/sketchwright-mcp/docs/architecture/Schema.md) | Provides the data schema that must be synchronized upon any model modification. |
| [API.md](file:///f:/GITHUB/sketchwright-mcp/docs/architecture/API.md) | Defines the contract interfaces protected by repository rules. |
| [SecurityAndCompliance.md](file:///f:/GITHUB/sketchwright-mcp/docs/guides/SecurityAndCompliance.md) | Expands upon the security baseline rules defined in Section 5. |
| [Testing.md](file:///f:/GITHUB/sketchwright-mcp/docs/development/testing.md) | Details the test suites and coverage requirements mandated by `RULE-007`. |
| [Deployment.md](file:///f:/GITHUB/sketchwright-mcp/docs/guides/Deployment.md) | Outlines release and CI/CD operations governed by Section 3. |
| [Glossary.md](file:///f:/GITHUB/sketchwright-mcp/docs/product/Glossary.md) | Defines terminology referenced throughout these rules. |
