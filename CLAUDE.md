# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

`ga-bench` is a benchmark framework for running and evaluating AI agents on tasks. Agents are executed against a task set and graded by an LLM-as-judge evaluator.

## Architecture

**Core:**
- **`run.py`** — CLI entry point (typer). Two mandatory args: `agent` (enum) and `tasks_dir` (path).
- **`agents/`** — Agent implementations. Each exposes `async def get_agent() -> Agent`. The `Agent` protocol is in `agents/base.py`.
- **`tasks/`** — Task loading and models. Tasks are JSON files with `domain`, `prompt`, `gold_response`, `rubric`.
- **`evaluator/`** — LLM-as-judge evaluation. `evaluate_run(run_id)` reads agent outputs and writes grades.

**Helpers (planned, not yet implemented):**
- **Worlds** — MCP-first tool collections defining an agent's operating environment
- **Skills** — Reusable instruction sets for agents

## File Map

```
run.py                        CLI (typer), AgentName enum, task loop
agents/base.py                Agent protocol
agents/types.py               AgentResult, TokenUsage
agents/langchain/react.py     LangChain ReAct agent
agents/langchain/deepagent.py LangChain Deep Agent
tasks/types.py                Task, Rubric (Pydantic models)
tasks/helpers.py              load_tasks(dir) → list[Task]
evaluator/evaluate.py         llm_as_judge(), evaluate_run()
evaluator/types.py            EvalResult, JudgmentResult, TaskGrade, FinalSummary
```

## Running the project

Always use `uv run --group langchain` — the agent and evaluator dependencies are in the `langchain` group:

```bash
# Run an agent
uv run --group langchain python run.py langchain-react tasks/examples

# Evaluate a run
uv run --group langchain python -m evaluator.evaluate <run_id>
```

## Key conventions

- **Model strings** use LangChain's `init_chat_model` format: `google_genai:gemini-...`, `anthropic:claude-...`. Set via `AGENT_MODEL` / `JUDGE_MODEL` env vars (`.env` file).
- **Gemini content quirk**: Gemini returns `message.content` as a list of blocks (`[{"type": "text", "text": "..."}]`) instead of a plain string. Both agent implementations handle this — new agents targeting Gemini must do the same.
- **Logging**: Use `loguru` (`from loguru import logger`). Levels: `INFO` for progress steps, `DEBUG` for verbose detail, `SUCCESS` for completions.
- **Output structure**: `output/<run_id>/` contains per-task JSONs, `.eval.json` eval results, `grades.json`, `final.json`, `manifest.json`.

## Adding a new agent

1. Create `agents/<framework>/<name>.py` with `async def get_agent() -> Agent`
2. Implement `async def run(task: Task, system_prompt: str = "") -> AgentResult`
3. Add to `AgentName` enum in `run.py` and a branch in `_get_agent()`

## Dependencies

- Base: `pydantic`, `typer`, `loguru`
- Langchain group: `langchain`, `langchain-anthropic`, `langchain-google-vertexai`, `deepagents`, `openevals`
