from pydantic import BaseModel


class TokenUsage(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0


class AgentResult(BaseModel):
    response: str
    token_usage: TokenUsage
    time_taken: float  # seconds
