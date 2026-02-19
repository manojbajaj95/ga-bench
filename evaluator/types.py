from pydantic import BaseModel
from agents.types import TokenUsage


class JudgmentResult(BaseModel):
    criterion: str
    score: bool
    comment: str


class EvalResult(BaseModel):
    judgments: list[JudgmentResult]
    passed: int
    total: int


class TaskGrade(BaseModel):
    task_id: str
    domain: str
    prompt: str
    score: float          # passed / total
    passed: int
    total: int
    token_usage: TokenUsage
    time_taken: float


class FinalSummary(BaseModel):
    run_id: str
    num_tasks: int
    avg_score: float
    avg_time_taken: float
    total_token_usage: TokenUsage
    avg_token_usage: TokenUsage
