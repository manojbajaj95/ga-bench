import os
import time
from typing import Any

from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient, ResultMessage  # type: ignore[import-untyped]
from loguru import logger

from agents.types import AgentResult, TokenUsage
from tasks.types import Task

# Server name used as the MCP namespace in allowed_tools
_MCP_SERVER_NAME = "world"


class ClaudeAgentSDKAgent:
    def __init__(self, mcp_server: dict[str, Any] | None = None):
        # Agent SDK uses plain model IDs; strip provider prefix if present
        # e.g. "anthropic:claude-haiku-4-5" -> "claude-haiku-4-5"
        model_env = os.getenv("AGENT_MODEL", "claude-haiku-4-5")
        if ":" in model_env:
            model_env = model_env.split(":", 1)[1]
        self._model = model_env
        self._mcp_server = mcp_server
        logger.debug("ClaudeAgentSDKAgent using model: {}", self._model)
        if mcp_server:
            logger.debug("MCP server configured: {}", mcp_server.get("url"))

    def _build_options(self, system_prompt: str) -> ClaudeAgentOptions:
        kwargs: dict[str, Any] = {
            "model": self._model,
            "system_prompt": system_prompt if system_prompt else None,
            "permission_mode": "bypassPermissions",
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
                if usage:
                    inp = usage.get("input_tokens", 0) or 0
                    out = usage.get("output_tokens", 0) or 0
                    token_usage = TokenUsage(
                        input_tokens=token_usage.input_tokens + inp,
                        output_tokens=token_usage.output_tokens + out,
                        total_tokens=token_usage.total_tokens + inp + out,
                    )

        elapsed = round(time.perf_counter() - start, 3)
        return AgentResult(
            response=response_text,
            token_usage=token_usage,
            time_taken=elapsed,
        )


async def get_agent(mcp_server: dict[str, Any] | None = None) -> ClaudeAgentSDKAgent:
    return ClaudeAgentSDKAgent(mcp_server=mcp_server)


if __name__ == "__main__":
    import asyncio

    from tasks.types import Task

    async def main():
        agent = await get_agent()
        task = Task(domain="test", prompt="What is 2 + 2?", gold_response="4", rubric=[])
        result = await agent.run(task)
        print(result)

    asyncio.run(main())
