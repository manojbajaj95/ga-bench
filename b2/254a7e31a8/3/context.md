# Session Context

## User Prompts

### Prompt 1

Implement the following plan:

# Plan: Add Python Best Practices Tooling

## Context
ga-bench has no linting, formatting, type checking, or pre-commit hooks. Code already has good type hints and Pydantic models. Adding ruff + ty + pre-commit enforces consistent quality automatically.

## Changes

### 1. `pyproject.toml` — add dev group + tool configs

**Add dev dependency group:**
```toml
[dependency-groups]
dev = [
    "pre-commit>=4.0.0",
    "ruff>=0.9.0",
    "ty>=0.0.1a3",
]
```

**Add ru...

### Prompt 2

commit this

