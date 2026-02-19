# ga-bench

A benchmark framework for running and evaluating AI agents on tasks. Agents are executed against a task set and graded by an LLM-as-judge evaluator.

## Architecture

```
run.py              — CLI entry point (typer)
agents/             — Agent implementations
  base.py           — Agent protocol (interface)
  types.py          — AgentResult, TokenUsage
  langchain/
    react.py        — LangChain ReAct agent
    deepagent.py    — LangChain Deep Agent
tasks/              — Task definitions
  types.py          — Task, Rubric models
  helpers.py        — load_tasks()
  examples/         — Sample task JSON files
evaluator/          — LLM-as-judge evaluation
  evaluate.py       — evaluate_run()
  types.py          — EvalResult, TaskGrade, FinalSummary
output/             — Run results (gitignored)
  <run_id>/
    <task_id>.json      — Per-task agent output
    <task_id>.eval.json — Per-task evaluation
    grades.json         — All task grades
    final.json          — Aggregated summary
    manifest.json       — Run metadata
```

## Setup

```bash
# Install base dependencies
uv sync

# Install with langchain agents
uv sync --group langchain
```

Configure environment variables in `.env`:

```env
AGENT_MODEL=google_genai:gemini-2.0-flash   # model used by the agent
JUDGE_MODEL=google_genai:gemini-2.0-flash   # model used by the evaluator
```

Model strings use LangChain's `init_chat_model` format: `<provider>:<model-id>`.

## Running agents

```bash
uv run --group langchain python run.py <agent> <tasks-dir> [options]
```

**Agents:**
- `langchain-react` — LangChain ReAct agent
- `langchain-deepagent` — LangChain Deep Agent

**Options:**
- `--output / -o` — output directory (default: `output/`)
- `--system-prompt / -s` — system prompt passed to the agent

**Examples:**

```bash
# Run react agent on example tasks
uv run --group langchain python run.py langchain-react tasks/examples

# Run deepagent with custom output dir
uv run --group langchain python run.py langchain-deepagent tasks/examples -o runs/

# Run with a system prompt
uv run --group langchain python run.py langchain-react tasks/examples -s "Be concise."
```

## Evaluating a run

```bash
uv run --group langchain python -m evaluator.evaluate <run_id>
```

Reads agent outputs from `output/<run_id>/`, judges each task against its rubric, and writes `grades.json` and `final.json`.

## Task format

Tasks are JSON files with this schema:

```json
{
  "domain": "mathematics",
  "prompt": "What is fib(10)?",
  "gold_response": "55",
  "rubric": [
    { "criteria": "The exact value 55 should be stated" }
  ]
}
```

## Adding a new agent

1. Create `agents/<framework>/<name>.py` implementing `async def get_agent() -> Agent`
2. The agent class must implement `async def run(task: Task, system_prompt: str = "") -> AgentResult`
3. Add an entry to `AgentName` enum in `run.py` and a matching branch in `_get_agent()`

## Known issues / quirks

- Gemini returns `content` as a list of blocks (`[{"type": "text", "text": "..."}]`) rather than a plain string. Both `react.py` and `deepagent.py` handle this by joining text blocks.
- `JUDGE_MODEL` / `AGENT_MODEL` use LangChain's provider-prefixed format (e.g. `google_genai:...`, `anthropic:...`).
- LangChain agent dependencies are in the `langchain` dependency group — always run with `--group langchain`.
