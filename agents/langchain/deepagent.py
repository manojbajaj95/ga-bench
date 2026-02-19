import os
import time

from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model

from agents.types import AgentResult, TokenUsage
from tasks.types import Task


class DeepAgent:
    def __init__(self):
        model_id = os.getenv("AGENT_MODEL", "anthropic:claude-haiku-4-5")
        self._agent = create_deep_agent(model=init_chat_model(model_id))

    async def run(self, task: Task, system_prompt: str = "") -> AgentResult:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": task.prompt})

        start = time.perf_counter()
        result = self._agent.invoke({"messages": messages})
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


async def get_agent() -> DeepAgent:
    return DeepAgent()


if __name__ == "__main__":
    import asyncio

    from tasks.types import Task

    async def main():
        agent = await get_agent()
        task = Task(domain="test", prompt="hi", gold_response="", rubric=[])
        result = await agent.run(task)
        print(result)

    asyncio.run(main())
