import os
from typing import List

import pytest
from dotenv import load_dotenv
from langchain_community.tools import ShellTool
from langchain_core.tools import BaseTool
from loguru import logger

from src.core.entity.tools_server import ToolsServer
from src.service.react_agent.entity.react_agent_request import ReActAgentRequest
from src.service.react_agent.graph.react_agent_graph import ReActAgentGraph


@pytest.mark.asyncio
async def test_react_agent_without_tools():
    tools_servers: List[ToolsServer] = [
        ToolsServer(name="time",url='langchain:current_time'),
        ToolsServer(name="duckduckgo", url='langchain:duckduckgo')
        # MCPServer(name="time mcp", url="http://127.0.0.1:17000/sse"),
    ]
    request = ReActAgentRequest(
        model="gpt-4o",
        openai_api_base=os.getenv("OPENAI_BASE_URL"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        user_message=f"""
            今天有什么AI相关的新闻
        """,
        user_id="umr",
        thread_id="2",
        tools_servers=tools_servers,
    )
    graph = ReActAgentGraph()
    result = await graph.execute(request)
    logger.info(result)
