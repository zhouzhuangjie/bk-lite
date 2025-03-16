import uuid
from typing import List

from langserve import CustomUserType

from apps.chat_service.user_types.chat_history import ChatHistory
from apps.chat_service.user_types.mcp_server import McpServer


class OpenAIChatRequest(CustomUserType):
    openai_api_base: str = 'https://api.openai.com'
    openai_api_key: str
    model: str = 'gpt-4o'

    system_message_prompt: str = ''
    temperature: float = 0.7
    user_message: str
    chat_history: List[ChatHistory]

    conversation_window_size: int = 10
    rag_context: str = ''

    mcp_servers: List[McpServer] = []

    trace_id: str = str(uuid.uuid4())
