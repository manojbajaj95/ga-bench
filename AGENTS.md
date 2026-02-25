# PROJECT KNOWLEDGE BASE

**Generated:** 2026-02-25
**Type:** ga-bench (AI Agent Benchmark Framework)

## OVERVIEW
`ga-bench` is a benchmark framework for evaluating AI agents using an LLM-as-judge approach. It executes agents against tasks in a simulated "world" (MCP server) and grades their performance.

## STRUCTURE
```
.
├── agents/       # Agent implementations (LangChain, Claude SDK)
├── tasks/        # Task definitions (JSON) & rubrics
├── worlds/       # MCP server & simulated apps (Email, Calendar, etc.)
├── evaluator/    # LLM-as-judge evaluation logic
└── run.py        # CLI entry point (Task runner)
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| **Run Benchmark** | `run.py` | CLI entry point; manages lifecycle |
| **Add Agent** | `agents/<framework>/` | Implement `get_agent()` & `run()` |
| **Add Tool/App** | `worlds/apps/` | Create class + `create_mcp_server()` |
| **Add Task** | `tasks/worlds/` | JSON file with prompt & rubric |
| **Evaluation** | `evaluator/evaluate.py` | Logic for grading agent output |

## CONVENTIONS
- **Dependency Mgmt**: `uv` is mandatory. Use `uv sync --group langchain`.
- **Logging**: `loguru` (INFO=progress, DEBUG=verbose). NO `print()`.
- **Type Checking**: `ty` (wrapper around `pyright`?).
- **Formatting**: `ruff` (120 chars, double quotes).
- **Async**: All agent/world interactions are `async`/`await`.
- **Gemini Quirk**: Handle `message.content` as list of blocks `[{"type": "text", ...}]`.
- **MCP Namespacing**: Tools must be `<app>_<method>` (e.g., `email_send_email`).

## ANTI-PATTERNS (THIS PROJECT)
- **DO NOT** use `print()` for logging (swallowed or clutters output).
- **DO NOT** hardcode port `7331` (use constant, but avoid conflicts).
- **DO NOT** assume Judge sees World state (Judge sees ONLY agent text).
- **DO NOT** write prompts without explicit output format instructions.

## COMMANDS
```bash
# Run agent on world tasks
uv run --group langchain python run.py langchain-react tasks/worlds --world worlds/server.py

# Evaluate a run
uv run --group langchain python -m evaluator.evaluate <run_id>
```
