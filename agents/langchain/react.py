import os
import time
from typing import Any

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import BaseTool
from loguru import logger

from agents.types import AgentResult, TokenUsage
from tasks.types import Task


def _msg_type(msg: Any) -> str:
    if isinstance(msg, AIMessage):
        return "AI"
    if isinstance(msg, HumanMessage):
        return "HUMAN"
    if isinstance(msg, SystemMessage):
        return "SYSTEM"
    if isinstance(msg, ToolMessage):
        return "TOOL"
    return type(msg).__name__.upper()


def _msg_content(msg: Any) -> str:
    content = msg.content
    if isinstance(content, list):
        content = "".join(block.get("text", "") if isinstance(block, dict) else str(block) for block in content)
    parts = [content] if content else []
    if isinstance(msg, AIMessage) and msg.tool_calls:
        for tc in msg.tool_calls:
            parts.append(f"<tool_call name={tc['name']} args={tc['args']}>")
    if isinstance(msg, ToolMessage):
        parts = [f"<tool_result name={msg.name} tool_call_id={msg.tool_call_id}> {content}"]
    return "\n".join(parts)


class ReactAgent:
    def __init__(self, tools: list[BaseTool] | None = None):
        model = os.getenv("AGENT_MODEL", "anthropic:claude-haiku-4-5")
        self._agent = create_agent(model, tools=tools or []).with_config({"recursion_limit": 25})

    async def run(self, task: Task, system_prompt: str = "") -> AgentResult:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": task.prompt})

        start = time.perf_counter()
        result = await self._agent.ainvoke({"messages": messages})
        elapsed = round(time.perf_counter() - start, 3)

        messages = result["messages"]
        input_tokens = 0
        output_tokens = 0
        total_tokens = 0
        for msg in messages:
            usage = getattr(msg, "usage_metadata", None) or {}
            input_tokens += usage.get("input_tokens", 0)
            output_tokens += usage.get("output_tokens", 0)
            total_tokens += usage.get("total_tokens", 0)
            logger.debug(
                "[{msg_type}] tokens=({input_tokens}in/{output_tokens}out) {content}",
                msg_type=_msg_type(msg),
                content=_msg_content(msg),
                input_tokens=usage.get("input_tokens"),
                output_tokens=usage.get("output_tokens"),
                total_tokens=usage.get("total_tokens"),
            )

        last_msg = messages[-1]
        content = last_msg.content
        if isinstance(content, list):
            content = "".join(block.get("text", "") if isinstance(block, dict) else str(block) for block in content)

        return AgentResult(
            response=content,
            token_usage=TokenUsage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
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
