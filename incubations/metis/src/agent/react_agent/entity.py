from typing import List

from src.core.entity import MCPServer, BasicLLMReuqest, BasicLLMResponse


class ReActAgentResponse(BasicLLMResponse):
    pass


class ReActAgentRequest(BasicLLMReuqest):
    mcp_servers: List[MCPServer] = []
