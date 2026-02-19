from typing import Protocol, runtime_checkable

from tasks.types import Task

from .types import AgentResult


@runtime_checkable
class Agent(Protocol):
    async def run(self, task: Task, system_prompt: str = "") -> AgentResult: ...
