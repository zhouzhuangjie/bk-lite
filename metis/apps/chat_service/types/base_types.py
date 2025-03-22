from typing import Any, Dict, Protocol, AsyncIterator
from apps.chat_service.user_types.chat_history import ChatHistory
from apps.chat_service.user_types.mcp_server import McpServer
from typing import List

class IOpenAIDriver(Protocol):
    """OpenAI 驱动接口定义"""
    def is_streaming(self) -> bool: ...
    
    async def execute_with_tools(self, user_message: str, message_history: Any,
                               system_prompt: str, rag_content: str,
                               mcp_servers: List[McpServer]): ...
    
    def invoke_simple_chain(self, user_message: str, message_history: Any,
                          system_prompt: str, rag_content: str,
                          trace_id: str, image_data: List[str]) -> Dict: ...
