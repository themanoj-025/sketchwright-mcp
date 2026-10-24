| Field | Value |
|---|---|
| Version | v1.0.0 |
| Last Updated | 2026-10-24 |
| Owner | Principal Architect & Risk Manager |
| Status | Approved (Live) |

# 📄 Operational & Technical Risk Register (RiskRegister) — Sketchwright

## 1. Executive Risk Landscape
As a zero-network, mathematical layout and serialization engine, Sketchwright’s primary risks reside in **geometric edge cases (crossings, cycle explosion)**, **stdio stream corruption in AI host environments**, and **schema drift with upstream Excalidraw releases**.

---

## 2. Risk Matrix & Quadrant Visualization

```mermaid
quadrantChart
    title Operational & Algorithmic Risk Matrix
    x-axis Low Impact --> High Impact
    y-axis Low Likelihood --> High Likelihood
    quadrant-1 Severe (Immediate Action Required)
    quadrant-2 Operational Watch (Active Monitoring)
    quadrant-3 Low Risk (Acceptable / Managed)
    quadrant-4 Critical Contingency (Contingency Plan)
    "RSK-001 Stdout Corruption": [0.85, 0.40]
    "RSK-002 Upstream Schema Drift": [0.75, 0.50]
    "RSK-003 Cycle Ranking Hang": [0.90, 0.20]
    "RSK-004 Font Metric Mismatch": [0.45, 0.60]
    "RSK-005 Malicious Input DoS": [0.80, 0.25]
    "RSK-006 Path Traversal Vulnerability": [0.95, 0.15]
```

---

## 3. Comprehensive Risk Inventory

| Risk ID | Risk Title & Description | Likelihood (1–5) | Impact (1–5) | Risk Score | Preventative Mitigation Strategy | Contingency Plan | Owner | Status |
|---|---|:---:|:---:|:---:|---|---|---|:---:|
| `RSK-001` | **Stdout Stream Corruption**<br/>Debug or library logging writes raw text to `stdout`, invalidating JSON-RPC framing in Claude Desktop or Cursor. | 2 | 5 | **10** | Configure root loggers to write strictly to `sys.stderr`. Wrap entry points in stdio hygiene interceptors. | Catch pipe errors and emit structured MCP error envelopes. | Protocols Dev | **Mitigated** |
| `RSK-002` | **Upstream Excalidraw Schema Drift**<br/>Excalidraw modifies required element keys, container bindings, or roundness types in v2/v3 schemas. | 3 | 4 | **12** | Pin target schema version to Excalidraw v2. Run automated validation checks against official Excalidraw JSON schemas. | Provide schema compatibility adapter in serializer. | Core Dev | **Monitored** |
| `RSK-003` | **Cyclic Graph Layout Explosion**<br/>Complex multi-loop circular references cause recursion overflow or combinatorial explosion in crossing reduction. | 1 | 5 | **5** | Enforce DFS cycle breaking with deterministic back-edge reversal prior to layer assignment. Add timeout guards. | Fallback to topological grid layout if crossings exceed threshold. | Algorithm Dev | **Mitigated** |
| `RSK-004` | **Font Width Metric Discrepancy**<br/>Headless Python lacks native browser canvas font rendering, causing container text overflow in Excalidraw canvas. | 3 | 3 | **9** | Implement character-width heuristic tables with safety padding multipliers (+20% width buffer). | Allow manual width overrides via `NodeSpec.width`. | Core Dev | **Mitigated** |
| `RSK-005` | **Input Denial of Service (DoS)**<br/>Malicious or runaway AI agent passes 50MB JSON spec, exhausting host process memory. | 2 | 4 | **8** | Enforce hard 1 MB input size limit in CLI and FastMCP tool handlers. Cap graph at 500 nodes and 1,000 edges. | Return `413 Payload Too Large` error immediately. | SecOps Dev | **Mitigated** |
| `RSK-006` | **Path Traversal Overwrite**<br/>Malicious spec targets `../../sensitive.file` to overwrite host files. | 1 | 5 | **5** | Sanitize target paths using `os.path.realpath`, validating parent directory boundaries. | Reject relative paths containing traversal sequences. | SecOps Dev | **Mitigated** |
| `RSK-007` | **Dependency Supply Chain Vulnerability**<br/>Vulnerability introduced via upstream dependency update (`pydantic` or `mcp`). | 2 | 3 | **6** | Lock all dependencies with SHA-256 hashes in `uv.lock`. Run Dependabot and automated secret scans on every PR. | Freeze dependency versions and audit quarterly. | DevOps | **Monitored** |

---

## 4. Active Watch Items & Triggers

1. **Excalidraw Core Repository Releases**: Monitor upstream `excalidraw/excalidraw` GitHub releases for modifications to `ExcalidrawElement` schema.
2. **MCP SDK Updates**: Track changes in Anthropic's official `mcp` Python SDK to preserve stdio performance and protocol compatibility.
3. **Collision Rate in Complex DAGs**: Monitor fuzz testing collision rates on graphs exceeding 100 nodes.

---

## 5. Related Documents

| Document | Relationship & Cross-Reference |
|---|---|
| [PRD.md](file:///f:/GITHUB/sketchwright-mcp/docs/product/PRD.md) | Maps top project risks to product requirements and goals. |
| [TechSpec.md](file:///f:/GITHUB/sketchwright-mcp/docs/architecture/TechSpec.md) | Architectural defenses preventing risk materialization. |
| [AppFlow.md](file:///f:/GITHUB/sketchwright-mcp/docs/product/AppFlow.md) | Details error states and diagnostics associated with risk events. |
| [Design.md](file:///f:/GITHUB/sketchwright-mcp/docs/architecture/Design.md) | Mitigates font overflow risks through padding and typography tokens. |
| [Schema.md](file:///f:/GITHUB/sketchwright-mcp/docs/architecture/Schema.md) | Enforces field constraints defending against malformed input payloads. |
| [ImplementationPlan.md](file:///f:/GITHUB/sketchwright-mcp/docs/development/ImplementationPlan.md) | Schedules risk mitigation tasks (`TASK-4.1`, `TASK-4.2`). |
| [Tracker.md](file:///f:/GITHUB/sketchwright-mcp/docs/development/Tracker.md) | Records blockers and issues resulting from monitored risks. |
| [Rules.md](file:///f:/GITHUB/sketchwright-mcp/docs/development/Rules.md) | Codifies architectural rules that eliminate prohibited anti-patterns. |
| [API.md](file:///f:/GITHUB/sketchwright-mcp/docs/architecture/API.md) | Defines error response codes corresponding to risk triggers. |
| [SecurityAndCompliance.md](file:///f:/GITHUB/sketchwright-mcp/docs/guides/SecurityAndCompliance.md) | Details threat models corresponding to security risks. |
| [Testing.md](file:///f:/GITHUB/sketchwright-mcp/docs/development/testing.md) | Outlines automated regression tests that continuously test risk vectors. |
| [Deployment.md](file:///f:/GITHUB/sketchwright-mcp/docs/guides/Deployment.md) | Defines emergency rollback procedures for release-related risks. |
| [Glossary.md](file:///f:/GITHUB/sketchwright-mcp/docs/product/Glossary.md) | Defines terminology referenced in risk descriptions. |
