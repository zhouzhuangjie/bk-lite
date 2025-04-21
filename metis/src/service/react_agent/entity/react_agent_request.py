from typing import List

from langchain_core.tools import BaseTool

from src.core.entity.basic_llm_request import BasicLLMReuqest
from src.core.entity.mcp_server import MCPServer


class ReActAgentRequest(BasicLLMReuqest):
    mcp_servers: List[MCPServer] = []
    langchain_tools:List[str] = []