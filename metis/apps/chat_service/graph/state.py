from typing import List, TypedDict, Any

from apps.chat_service.user_types.chat_history import ChatHistory
from apps.chat_service.user_types.mcp_server import McpServer


class ChatState(TypedDict):
    """聊天状态定义"""
    user_message: str
    message_history: List[ChatHistory]
    system_prompt: str
    rag_content: str
    mcp_servers: List[McpServer]
    trace_id: str
    image_data: List[str]
    result: str
    input_tokens: int
    output_tokens: int
