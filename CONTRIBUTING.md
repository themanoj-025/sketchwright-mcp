# Contributing to Sketchwright

Thank you for your interest in contributing to Sketchwright!

## Code of Conduct
Please be polite, constructive, and respectful in all interactions.

## Development Workflow

### Prerequisites
- Python 3.12+
- `uv` package manager (`pip install uv` or `winget install astral-sh.uv`)

### Local Setup
```bash
git clone https://github.com/manoj-025/sketchwright-mcp.git
cd sketchwright-mcp
uv sync --all-groups
```

### Running Checks
Before submitting a pull request, ensure all local quality checks pass:

```bash
# Run test suite
uv run pytest -v

# Check formatting and style
uv run ruff format --check .
uv run ruff check .

# Static type checking
uv run mypy src

# Package build check
uv build
```

## Pull Request Guidelines
- Keep pull requests focused on a single change or cohesive feature.
- Ensure all new public functions have type annotations and unit test coverage.
- Do not introduce external dependencies without prior discussion.
- Preserve deterministic layout behavior and strict stdio discipline.
