import os
import time
from typing import Any

from langchain.agents import create_agent
from langchain_core.tools import BaseTool

from agents.types import AgentResult, TokenUsage
from tasks.types import Task


class ReactAgent:
    def __init__(self, tools: list[BaseTool] | None = None):
        model = os.getenv("AGENT_MODEL", "anthropic:claude-haiku-4-5")
        self._agent = create_agent(model, tools=tools or [])

    async def run(self, task: Task, system_prompt: str = "") -> AgentResult:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": task.prompt})

        start = time.perf_counter()
        result = await self._agent.ainvoke({"messages": messages})
        elapsed = round(time.perf_counter() - start, 3)

        last_msg = result["messages"][-1]
        usage = getattr(last_msg, "usage_metadata", None) or {}

        content = last_msg.content
        if isinstance(content, list):
            content = "".join(block.get("text", "") if isinstance(block, dict) else str(block) for block in content)

        return AgentResult(
            response=content,
            token_usage=TokenUsage(
                input_tokens=usage.get("input_tokens", 0),
                output_tokens=usage.get("output_tokens", 0),
                total_tokens=usage.get("total_tokens", 0),
            ),
            time_taken=elapsed,
        )


async def get_agent(mcp_server: dict[str, Any] | None = None) -> ReactAgent:
    tools: list[BaseTool] = []
    if mcp_server:
        from langchain_mcp_adapters.client import MultiServerMCPClient, StreamableHttpConnection

        connection: StreamableHttpConnection = {
            "transport": mcp_server["transport"],
            "url": mcp_server["url"],
        }
        client = MultiServerMCPClient({"world": connection})
        tools = await client.get_tools()
    return ReactAgent(tools=tools)


if __name__ == "__main__":
    import asyncio

    from tasks.types import Task

    async def main():
        agent = await get_agent()
        task = Task(domain="test", prompt="hi", gold_response="", rubric=[])
        result = await agent.run(task)
        print(result)

    asyncio.run(main())
