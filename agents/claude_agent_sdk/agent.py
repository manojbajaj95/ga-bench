import os
import time

from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient, ResultMessage  # type: ignore[import-untyped]
from loguru import logger

from agents.types import AgentResult, TokenUsage
from tasks.types import Task


class ClaudeAgentSDKAgent:
    def __init__(self):
        # Agent SDK uses plain model IDs; strip provider prefix if present
        # e.g. "anthropic:claude-haiku-4-5" -> "claude-haiku-4-5"
        model_env = os.getenv("AGENT_MODEL", "claude-haiku-4-5")
        if ":" in model_env:
            model_env = model_env.split(":", 1)[1]
        self._model = model_env
        logger.debug("ClaudeAgentSDKAgent using model: {}", self._model)

    async def run(self, task: Task, system_prompt: str = "") -> AgentResult:
        options = ClaudeAgentOptions(
            model=self._model,
            system_prompt=system_prompt if system_prompt else None,
            allowed_tools=["Read", "Edit", "Glob", "Bash", "Grep"],
            permission_mode="bypassPermissions",
        )

        start = time.perf_counter()
        response_text = ""
        token_usage = TokenUsage()

        async with ClaudeSDKClient(options=options) as client:
            await client.query(task.prompt)
            async for message in client.receive_response():
                if isinstance(message, ResultMessage):
                    if message.result:
                        response_text = message.result
                    if message.usage:
                        inp = message.usage.get("input_tokens", 0) or 0
                        out = message.usage.get("output_tokens", 0) or 0
                        token_usage = TokenUsage(
                            input_tokens=inp,
                            output_tokens=out,
                            total_tokens=inp + out,
                        )

        elapsed = round(time.perf_counter() - start, 3)
        return AgentResult(
            response=response_text,
            token_usage=token_usage,
            time_taken=elapsed,
        )


async def get_agent() -> ClaudeAgentSDKAgent:
    return ClaudeAgentSDKAgent()


if __name__ == "__main__":
    import asyncio

    from tasks.types import Task

    async def main():
        agent = await get_agent()
        task = Task(domain="test", prompt="What is 2 + 2?", gold_response="4", rubric=[])
        result = await agent.run(task)
        print(result)

    asyncio.run(main())
