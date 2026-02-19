import asyncio
import json
import uuid
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path

import typer
from dotenv import load_dotenv
from loguru import logger

load_dotenv()  # Load .env before importing modules that may read env vars at import time

from agents.base import Agent  # noqa: E402
from tasks import load_tasks  # noqa: E402
from tasks.types import Task  # noqa: E402

app = typer.Typer()


class AgentName(StrEnum):
    langchain_react = "langchain-react"
    langchain_deepagent = "langchain-deepagent"
    claude_agent_sdk = "claude-agent-sdk"


async def _get_agent(name: AgentName) -> Agent:
    logger.info("Loading agent: {}", name.value)
    if name == AgentName.langchain_react:
        from agents.langchain.react import get_agent
    elif name == AgentName.langchain_deepagent:
        from agents.langchain.deepagent import get_agent
    elif name == AgentName.claude_agent_sdk:
        from agents.claude_agent_sdk.agent import get_agent
    agent = await get_agent()
    logger.success("Agent loaded: {}", name.value)
    return agent


async def run_task(agent: Agent, task: Task, system_prompt: str = "") -> dict:
    logger.info("[{}] Running task: {}", task.domain, task.prompt[:80])
    result = await agent.run(task, system_prompt=system_prompt)
    logger.success(
        "[{}] Done — tokens={} time={}s",
        task.domain,
        result.token_usage.total_tokens,
        result.time_taken,
    )
    return {
        "task_id": task.id,
        "domain": task.domain,
        "prompt": task.prompt,
        "gold_response": task.gold_response,
        "rubric": [r.criteria for r in task.rubric],
        "agent_response": result.response,
        "token_usage": result.token_usage.model_dump(),
        "time_taken": result.time_taken,
    }


async def _main(agent_name: AgentName, tasks_dir: str, output_base: str, system_prompt: str):
    run_id = str(uuid.uuid4())
    run_dir = Path(output_base) / run_id
    run_dir.mkdir(parents=True)

    logger.info("Run ID:  {}", run_id)
    logger.info("Output:  {}", run_dir)

    agent = await _get_agent(agent_name)
    tasks = load_tasks(tasks_dir)
    logger.info("Tasks:   {} loaded from {}", len(tasks), tasks_dir)

    results = []
    for i, task in enumerate(tasks, 1):
        logger.info("Task {}/{}", i, len(tasks))
        result = await run_task(agent, task, system_prompt=system_prompt)
        logger.debug("Response: {}", result["agent_response"][:120])

        task_file = run_dir / f"{task.id}.json"
        task_file.write_text(json.dumps(result, indent=2))
        results.append(result)

    manifest = {
        "run_id": run_id,
        "timestamp": datetime.now(UTC).isoformat(),
        "agent": agent_name.value,
        "tasks_dir": tasks_dir,
        "num_tasks": len(results),
        "task_ids": [r["task_id"] for r in results],
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    logger.success("Done. Results saved to {}/", run_dir)


@app.command()
def main(
    agent: AgentName = typer.Argument(..., help="Agent to run"),  # noqa: B008
    tasks_dir: str = typer.Argument(..., help="Path to the tasks directory"),  # noqa: B008
    output: str = typer.Option("output", "--output", "-o", help="Base output directory"),
    system_prompt: str = typer.Option("", "--system-prompt", "-s", help="System prompt passed to the agent"),
):
    asyncio.run(_main(agent, tasks_dir, output, system_prompt))


if __name__ == "__main__":
    app()
