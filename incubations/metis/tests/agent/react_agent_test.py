import os
from typing import List

import pytest
from dotenv import load_dotenv

from src.agent.react_agent.entity import ReActAgentRequest
from src.agent.react_agent.graph import ReActAgentGraph
from src.core.entity import MCPServer

load_dotenv()


@pytest.mark.asyncio
async def test_react_agent_without_tools():
    mcp_servers: List[MCPServer] = [
        MCPServer(name="time mcp", url="http://127.0.0.1:17000/sse"),
    ]

    request = ReActAgentRequest(
        model="gpt-4o",
        openai_api_base=os.getenv("OPENAI_BASE_URL"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        user_message="现在的时间是几点",
        user_id="1",
        thread_id="2",
        mcp_servers=mcp_servers
    )
    graph = ReActAgentGraph()
    result = await graph.execute(request)
    print(result)
