from pydantic import BaseModel


class ChatBotWorkflowResponse(BaseModel):
    message: str
    total_tokens: int


class ChatBotWorkflowRequest(BaseModel):
    openai_api_base: str = 'https://api.openai.com'
    openai_api_key: str = ''
    model: str = 'gpt-4o'

    system_message_prompt: str = ''
    temperature: float = 0.7

    user_message: str = ''
    total_tokens: int = 0

    user_id: str
    thread_id: str
