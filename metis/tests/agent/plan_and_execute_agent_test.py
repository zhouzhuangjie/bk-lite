import os
from typing import List

import pytest
from loguru import logger

from src.agent.plan_and_execute_agent.plan_and_execute_agent_graph import PlanAndExecuteAgentGraph
from src.core.entity.tools_server import ToolsServer
from src.entity.agent.plan_and_execute_agent_request import PlanAndExecuteAgentRequest

@pytest.mark.asyncio
async def test_compile_graph():
    tools_servers: List[ToolsServer] = [
        ToolsServer(name="current_time", url='langchain:current_time'),
    ]

    request = PlanAndExecuteAgentRequest(
        model="gpt-4o",
        openai_api_base=os.getenv("OPENAI_BASE_URL"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        user_message="今天是星期几",
        user_id="umr",
        thread_id="2",
        tools_servers=tools_servers,
        extra_config={
            "jenkins_url": os.getenv("TEST_JENKINS_URL"),
            "jenkins_username": os.getenv("TEST_JENKINS_USERNAME"),
            "jenkins_password": os.getenv("TEST_JENKINS_PASSWORD"),
        }
    )
    graph = PlanAndExecuteAgentGraph()
    result = await graph.execute(request)
    logger.info(result)
