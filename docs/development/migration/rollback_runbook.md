# Rollback Runbook: Restructuring Protocol v3.0

Audience: On-call engineer or repository maintainer.

## 1. Quick Revert
Because all files were retained in their canonical positions without destructive mutations:
- **Git Branch**: `restructure/sketchwright/work`
- **Baseline Tag**: `restructure/sketchwright/baseline`

To reset to exact baseline state:
```bash
git checkout restructure/sketchwright/baseline
```

## 2. Verification
After any checkout or revert, run the tier-F verification gate:
```bash
uv run pytest -q
uv run ruff check .
uv run mypy src/sketchwright
```
