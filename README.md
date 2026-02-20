# ga-bench

A benchmark framework for running and evaluating AI agents on tasks. Agents are executed against a task set and graded by an LLM-as-judge evaluator.

## Architecture

```
run.py              — CLI entry point (typer), world server lifecycle
agents/             — Agent implementations
  base.py           — Agent protocol (interface)
  types.py          — AgentResult, TokenUsage
  langchain/
    react.py        — LangChain ReAct agent (MCP-aware)
    deepagent.py    — LangChain Deep Agent
tasks/              — Task definitions
  types.py          — Task, Rubric models
  helpers.py        — load_tasks()
  examples/         — Simple factual tasks (no world)
  worlds/           — Agentic tasks requiring world tools
evaluator/          — LLM-as-judge evaluation
  evaluate.py       — evaluate_run()
  types.py          — EvalResult, TaskGrade, FinalSummary
worlds/             — MCP app servers
  server.py         — Main server, mounts all apps
  apps/
    email_app.py    — Email tools (list, get, send, delete, search…)
    calendar_app.py — Calendar tools (list, create, update, delete…)
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
uv sync --group langchain
```

Configure `.env`:

```env
AGENT_MODEL=google_genai:gemini-2.0-flash   # model used by the agent
JUDGE_MODEL=google_genai:gemini-2.0-flash   # model used by the evaluator
```

Model strings use LangChain's `init_chat_model` format: `<provider>:<model-id>`.

## Running agents

```bash
uv run --group langchain python run.py <agent> <tasks-dir> [options]
```

**Agents:** `langchain-react`, `langchain-deepagent`, `claude-agent-sdk`

**Options:**

| Flag | Description |
|---|---|
| `--world / -w` | Path to a world server script — starts it as an HTTP MCP server |
| `--output / -o` | Output directory (default: `output/`) |
| `--system-prompt / -s` | System prompt passed to the agent |

**Examples:**

```bash
# Simple factual tasks (no tools)
uv run --group langchain python run.py langchain-react tasks/examples

# Agentic tasks with a world (MCP tools)
uv run --group langchain python run.py langchain-react tasks/worlds --world worlds/server.py

# Custom output dir + system prompt
uv run --group langchain python run.py langchain-react tasks/worlds \
  --world worlds/server.py -o runs/ -s "Be concise."
```

When `--world` is provided, `run.py` starts the server on port `7331`, waits for it to be ready, and terminates it when the run completes. State persists across tool calls within a single run.

## Evaluating a run

```bash
uv run --group langchain python -m evaluator.evaluate <run_id>
```

Reads agent outputs from `output/<run_id>/`, judges each task criterion against the rubric using an LLM-as-judge, and writes `grades.json` and `final.json`.

## Task format

```json
{
  "id": "<uuid>",
  "domain": "email_management",
  "prompt": "Delete all spam emails. When done, report the number deleted and list each one by subject and ID.",
  "gold_response": "Deleted 1 spam email: 'You won a prize!' (e004).",
  "rubric": [
    { "criteria": "The agent must list or search the spam folder to find spam emails" },
    { "criteria": "The agent must delete every spam email found" },
    { "criteria": "The agent must report the count and subject/ID of deleted emails" }
  ]
}
```

### Prompt writing rules

1. **Specify the action AND the output format.** Without an explicit output instruction, agent responses are inconsistently terse or verbose and evaluations become flaky.

   | | Example |
   |---|---|
   | Bad | `"Delete all spam emails."` |
   | Good | `"Delete all spam emails. When done, report the number deleted and list each one by subject and ID."` |

2. **Be specific about scope** — e.g. "all emails in the spam folder" rather than "all emails".

3. **Match the world's seed data** — verify the task is solvable against the dummy data before writing the rubric.

### Rubric writing rules

1. **Each criterion must be verifiable from the agent's final text response alone.** The judge cannot re-query the world.
2. **Cover three layers:** discovery (did it find the right items?), mutation (did it perform the action?), reporting (did it state what it did?).
3. **Be concrete** — name the expected entities, counts, or IDs where possible.

## Adding a world app

Create `worlds/apps/<name>_app.py`:

```python
from fastmcp import FastMCP

class MyApp:
    def __init__(self) -> None:
        self.name = "myapp"       # becomes the tool namespace prefix

    def do_something(self, arg: str) -> dict:
        """One-line summary.

        Args:
            arg: What this arg is.
        Returns:
            dict: What is returned.
        Tags:
            tag1, tag2
        """
        return {"result": arg}

    def list_tools(self) -> list:
        return [self.do_something]

    def create_mcp_server(self) -> FastMCP:
        mcp = FastMCP(self.name)
        for fn in self.list_tools():
            mcp.tool()(fn)
        return mcp
```

Then add it to `worlds/server.py`:

```python
from worlds.apps.my_app import MyApp

_apps = [EmailApp(), CalendarApp(), MyApp()]
```

Tools are namespaced `<app.name>_<method_name>` (e.g. `myapp_do_something`).

## Adding a new agent

1. Create `agents/<framework>/<name>.py` with `async def get_agent(mcp_server: dict | None = None) -> Agent`
2. Implement `async def run(task: Task, system_prompt: str = "") -> AgentResult`
3. Use `mcp_server` (transport config dict) to connect via `MultiServerMCPClient` — see `react.py`
4. Add to `AgentName` enum in `run.py` and a branch in `_get_agent()`

## Known issues / quirks

- Gemini returns `content` as a list of blocks (`[{"type": "text", "text": "..."}]`) rather than a plain string. Both `react.py` and `deepagent.py` handle this — new Gemini agents must do the same.
- LangChain dependencies are in the `langchain` group — always run with `--group langchain`.
- The world server runs on a fixed port (`7331`). Running multiple benchmark instances simultaneously will conflict.
