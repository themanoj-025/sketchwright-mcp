# Installation Guide

Sketchwright requires Python 3.12 or newer. Windows is supported as a first-class operating environment alongside Linux and macOS.

## Installation via uv (Recommended)

`uv` provides fast, reproducible virtual environment management.

### Windows (PowerShell)

```powershell
# 1. Verify uv and Python
uv --version
uv python list

# 2. Clone repository
git clone https://github.com/manoj-025/sketchwright-mcp.git
Set-Location sketchwright-mcp

# 3. Synchronize virtual environment with all dependencies
uv sync --all-groups

# 4. Verify installation
uv run sketchwright --version
uv run sketchwright capabilities
```

### Linux / macOS (Bash / Zsh)

```bash
# 1. Clone repository
git clone https://github.com/manoj-025/sketchwright-mcp.git
cd sketchwright-mcp

# 2. Synchronize dependencies
uv sync --all-groups

# 3. Verify installation
uv run sketchwright --version
uv run sketchwright capabilities
```

## Building Wheel & Sdist

To build standard distributable wheels:

```bash
uv build
```

This creates:
- `dist/sketchwright-0.1.0-py3-none-any.whl`
- `dist/sketchwright-0.1.0.tar.gz`

You can install the wheel directly in any Python 3.12+ environment:
```bash
pip install dist/sketchwright-0.1.0-py3-none-any.whl
```
