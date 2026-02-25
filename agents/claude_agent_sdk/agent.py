import os
import time
from typing import Any

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
    SystemMessage,
    TextBlock,
    ThinkingBlock,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage,
)
from loguru import logger

from agents.types import AgentResult, TokenUsage
from tasks.types import Task


def _msg_type(msg: Any) -> str:
    if isinstance(msg, AssistantMessage):
        return "AI"
    if isinstance(msg, UserMessage):
        return "HUMAN"
    if isinstance(msg, SystemMessage):
        return "SYSTEM"
    if isinstance(msg, ResultMessage):
        return "RESULT"
    return type(msg).__name__.upper()


def _msg_content(msg: Any) -> str:
    content = getattr(msg, "content", None)
    if content is None:
        return getattr(msg, "result", "") or ""
    if isinstance(content, str):
        return content
    parts = []
    for block in content:
        if isinstance(block, TextBlock):
            parts.append(block.text)
        elif isinstance(block, ThinkingBlock):
            parts.append(f"<thinking>{block.thinking}</thinking>")
        elif isinstance(block, ToolUseBlock):
            parts.append(f"<tool_use name={block.name} input={block.input}>")
        elif isinstance(block, ToolResultBlock):
            result_content = block.content if isinstance(block.content, str) else str(block.content)
            parts.append(f"<tool_result tool_use_id={block.tool_use_id} is_error={block.is_error}> {result_content}")
        else:
            parts.append(str(block))
    return "\n".join(parts)


# Server name used as the MCP namespace in allowed_tools
_MCP_SERVER_NAME = "world"


class ClaudeAgentSDKAgent:
    def __init__(self, mcp_server: dict[str, Any] | None = None, max_turns: int = 25):
        # Agent SDK uses plain model IDs; strip provider prefix if present
        # e.g. "anthropic:claude-haiku-4-5" -> "claude-haiku-4-5"
        model_env = os.getenv("AGENT_MODEL", "claude-haiku-4-5")
        if ":" in model_env:
            model_env = model_env.split(":", 1)[1]
        self._model = model_env
        self._mcp_server = mcp_server
        self._max_turns = max_turns
        logger.debug("ClaudeAgentSDKAgent using model: {}", self._model)
        if mcp_server:
            logger.debug("MCP server configured: {}", mcp_server.get("url"))

    def _build_options(self, system_prompt: str) -> ClaudeAgentOptions:
        kwargs: dict[str, Any] = {
            "model": self._model,
            "system_prompt": system_prompt if system_prompt else None,
            "permission_mode": "bypassPermissions",
            "max_turns": self._max_turns,
        }

        if self._mcp_server:
            # Translate ga-bench transport config → SDK format
            kwargs["mcp_servers"] = {
                _MCP_SERVER_NAME: {
                    "type": "http",
                    "url": self._mcp_server["url"],
                }
            }
            # Wildcard: allow every tool exposed by the world server
            kwargs["allowed_tools"] = [f"mcp__{_MCP_SERVER_NAME}__*"]
        else:
            kwargs["allowed_tools"] = ["Read", "Edit", "Glob", "Bash", "Grep"]

        return ClaudeAgentOptions(**kwargs)

    async def run(self, task: Task, system_prompt: str = "") -> AgentResult:
        options = self._build_options(system_prompt)

        start = time.perf_counter()
        response_text = ""
        token_usage = TokenUsage()

        async with ClaudeSDKClient(options=options) as client:
            await client.query(task.prompt)
            async for message in client.receive_response():
                if isinstance(message, ResultMessage) and message.result:
                    response_text = message.result
                usage = getattr(message, "usage", None)
                inp, out = 0, 0
                if usage:
                    inp = usage.get("input_tokens", 0) or 0
                    out = usage.get("output_tokens", 0) or 0
                    token_usage = TokenUsage(
                        input_tokens=token_usage.input_tokens + inp,
                        output_tokens=token_usage.output_tokens + out,
                        total_tokens=token_usage.total_tokens + inp + out,
                    )
                logger.debug(
                    "[{msg_type}] tokens=({input_tokens}in/{output_tokens}out) {content}",
                    msg_type=_msg_type(message),
                    content=_msg_content(message),
                    input_tokens=inp or None,
                    output_tokens=out or None,
                    total_tokens=(inp + out) or None,
                )

        elapsed = round(time.perf_counter() - start, 3)
        return AgentResult(
            response=response_text,
            token_usage=token_usage,
            time_taken=elapsed,
        )


async def get_agent(mcp_server: dict[str, Any] | None = None) -> ClaudeAgentSDKAgent:
    return ClaudeAgentSDKAgent(mcp_server=mcp_server, max_turns=25)


if __name__ == "__main__":
    import asyncio

    from tasks.types import Task

    async def main():
        agent = await get_agent()
        task = Task(domain="test", prompt="What is 2 + 2?", gold_response="4", rubric=[])
        result = await agent.run(task)
        print(result)

    asyncio.run(main())
