from pydantic import BaseModel


class BasicLLMResponse(BaseModel):
    message: str
    total_tokens: int
