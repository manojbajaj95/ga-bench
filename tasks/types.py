import uuid

from pydantic import BaseModel, Field


class Rubric(BaseModel):
    criteria: str


class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    domain: str
    prompt: str
    gold_response: str
    rubric: list[Rubric]
