import uuid
from typing import List, Optional

from langserve import CustomUserType

from apps.chat_service.user_types.chat_history import ChatHistory


class ChatBotWorkflowResponse(CustomUserType):
    message: str
    total_tokens: int


class ChatBotWorkflowRequest(CustomUserType):
    openai_api_base: str = 'https://api.openai.com'
    openai_api_key: str
    model: str = 'gpt-4o'

    system_message_prompt: str = ''
    temperature: float = 0.7
    user_message: str = ''
    chat_history: List[ChatHistory] = []

    conversation_window_size: int = 10
    rag_context: str = ''

    image_data: List[str] = []
