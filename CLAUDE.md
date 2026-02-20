# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

`ga-bench` is a benchmark framework for running and evaluating AI agents on tasks. Agents are executed against a task set and graded by an LLM-as-judge evaluator.

## Architecture

**Core:**
- **`run.py`** — CLI entry point (typer). Mandatory args: `agent` (enum) and `tasks_dir` (path). Optional `--world` starts an MCP world server.
- **`agents/`** — Agent implementations. Each exposes `async def get_agent() -> Agent`. The `Agent` protocol is in `agents/base.py`.
- **`tasks/`** — Task loading and models. Tasks are JSON files with `domain`, `prompt`, `gold_response`, `rubric`.
- **`evaluator/`** — LLM-as-judge evaluation. `evaluate_run(run_id)` reads agent outputs and writes grades.
- **`worlds/`** — MCP app servers defining an agent's operating environment.

## File Map

```
run.py                        CLI (typer), AgentName enum, task loop, world server lifecycle
agents/base.py                Agent protocol
agents/types.py               AgentResult, TokenUsage
agents/langchain/react.py     LangChain ReAct agent (MCP-aware)
agents/langchain/deepagent.py LangChain Deep Agent
tasks/types.py                Task, Rubric (Pydantic models)
tasks/helpers.py              load_tasks(dir) → list[Task]
tasks/examples/               Simple factual tasks (no world)
tasks/worlds/                 World-based agentic tasks
evaluator/evaluate.py         llm_as_judge(), evaluate_run()
evaluator/types.py            EvalResult, JudgmentResult, TaskGrade, FinalSummary
worlds/server.py              Main MCP server — mounts all app sub-servers
worlds/apps/email_app.py      Email application (8 tools)
worlds/apps/calendar_app.py   Calendar application (8 tools)
```

## Running the project

Always use `uv run --group langchain` — agent and evaluator dependencies are in the `langchain` group:

```bash
# Run an agent on simple tasks (no world)
uv run --group langchain python run.py langchain-react tasks/examples

# Run an agent with a world (MCP tools)
uv run --group langchain python run.py langchain-react tasks/worlds --world worlds/server.py

# Evaluate a run
uv run --group langchain python -m evaluator.evaluate <run_id>
```

## Key conventions

- **Model strings** use LangChain's `init_chat_model` format: `google_genai:gemini-...`, `anthropic:claude-...`. Set via `AGENT_MODEL` / `JUDGE_MODEL` env vars (`.env` file).
- **Gemini content quirk**: Gemini returns `message.content` as a list of blocks (`[{"type": "text", "text": "..."}]`) instead of a plain string. Both agent implementations handle this — new agents targeting Gemini must do the same.
- **Logging**: Use `loguru` (`from loguru import logger`). Levels: `INFO` for progress steps, `DEBUG` for verbose detail, `SUCCESS` for completions.
- **Output structure**: `output/<run_id>/` contains per-task JSONs, `.eval.json` eval results, `grades.json`, `final.json`, `manifest.json`.
- **World server port**: Fixed at `WORLD_SERVER_PORT = 7331` in `run.py`.

## Adding a new agent

1. Create `agents/<framework>/<name>.py` with `async def get_agent(mcp_server: dict | None = None) -> Agent`
2. Implement `async def run(task: Task, system_prompt: str = "") -> AgentResult`
3. If the agent supports MCP tools, use `mcp_server` (the transport config dict) to connect — see `react.py` for the `MultiServerMCPClient` pattern
4. Add to `AgentName` enum in `run.py` and a branch in `_get_agent()`

## Adding a new world app

Create `worlds/apps/<name>_app.py` as a plain class — no base class needed:

```python
from fastmcp import FastMCP

class MyApp:
    def __init__(self) -> None:
        self.name = "myapp"           # used as MCP namespace prefix
        self._state = {}              # in-memory state persists per HTTP server lifecycle

    def my_tool(self, arg: str) -> dict:
        """Tool description.

        Args:
            arg: Description of arg.

        Returns:
            dict: Result description.

        Tags:
            tag1, tag2
        """
        return {"result": arg}

    def list_tools(self) -> list:
        return [self.my_tool]

    def create_mcp_server(self) -> FastMCP:
        mcp = FastMCP(self.name)
        for tool_fn in self.list_tools():
            mcp.tool()(tool_fn)
        return mcp
```

Then mount it in `worlds/server.py`:

```python
from worlds.apps.my_app import MyApp

_apps = [
    EmailApp(),
    CalendarApp(),
    MyApp(),       # tools appear as myapp_my_tool
]
```

Tools are namespaced as `<app.name>_<method_name>` (e.g. `email_list_emails`, `calendar_create_event`).

## Writing tasks

Tasks are JSON files in `tasks/<category>/`. Each task has:

```json
{
  "id": "<uuid>",
  "domain": "category_name",
  "prompt": "...",
  "gold_response": "...",
  "rubric": [
    { "criteria": "..." }
  ]
}
```

### Golden rules for prompts

1. **Specify both the action AND the output format.** The agent decides how terse or verbose to be — if the output format isn't explicit, the evaluator will get inconsistent results.

   **Bad:** `"Delete all spam emails."`
   **Good:** `"Delete all spam emails. When done, report the number deleted and list each one by subject and ID."`

2. **Be specific about the scope.** Ambiguous scope (e.g. "all emails") should be clarified (e.g. "all emails in the spam folder").

3. **Match the world state.** The prompt should be solvable against the dummy seed data in the app. Verify manually before writing the rubric.

### Golden rules for rubrics

1. **Each criterion must be independently verifiable from the agent's final text response alone.** The judge only sees the response — it cannot re-query the world state.

2. **Cover the full task:** typically 3 criteria: (1) discovery/search step, (2) mutation step (delete/create/update), (3) reporting step.

3. **Be concrete.** "The agent must report the email subject or ID" is better than "the agent must summarize what it did".

### Golden rules for gold_response

- Write what a correct, well-behaved agent would actually say — not a system log or a diff.
- Include the specific IDs/titles/counts from the seed data so the judge has a reference.
- Keep it concise: one or two sentences is enough.

## Dependencies

- Base: `pydantic`, `typer`, `loguru`, `fastmcp`
- Langchain group: `langchain`, `langchain-anthropic`, `langchain-google-vertexai`, `langchain-mcp-adapters`, `deepagents`, `openevals`
