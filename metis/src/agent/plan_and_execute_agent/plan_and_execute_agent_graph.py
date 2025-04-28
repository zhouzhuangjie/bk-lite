from typing import TypedDict
from venv import logger

from langchain_core.messages import ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.constants import END
from langgraph.graph import StateGraph, MessagesState

from src.agent.plan_and_execute_agent.plan_and_execute_agent_node import PlanAndExecuteAgentNode
from src.agent.plan_and_execute_agent.plan_and_execute_agent_state import PlanAndExecuteAgentState
from src.core.entity.basic_llm_response import BasicLLMResponse
from src.core.graph.tools_graph import ToolsGraph
from src.entity.agent.plan_and_execute_agent_request import PlanAndExecuteAgentRequest
from src.entity.agent.react_agent_request import ReActAgentRequest
from src.entity.agent.react_agent_response import ReActAgentResponse
from src.agent.react_agent.react_agent_node import ReActAgentNode
from src.agent.react_agent.react_agent_state import ReActAgentState
from langgraph.pregel import RetryPolicy
from loguru import logger


class PlanAndExecuteAgentGraph(ToolsGraph):

    async def compile_graph(self, request: PlanAndExecuteAgentRequest):
        node_builder = PlanAndExecuteAgentNode()

        await node_builder.setup(request)

        graph_builder = StateGraph(PlanAndExecuteAgentState)

        last_edge = self.prepare_graph(graph_builder, node_builder)

        graph_builder.add_node("agent", node_builder.execute_step, retry=RetryPolicy(max_attempts=5))
        graph_builder.add_node("planner", node_builder.plan_step)
        graph_builder.add_node("replan", node_builder.replan_step)

        graph_builder.add_edge(last_edge, "planner")

        graph_builder.add_edge("planner", "agent")
        graph_builder.add_edge("agent", "replan")
        graph_builder.add_conditional_edges(
            "replan",
            node_builder.should_end,
            ["agent", END],
        )

        graph = graph_builder.compile()
        return graph

    async def execute(self, request: ReActAgentRequest) -> ReActAgentResponse:
        graph = await self.compile_graph(request)
        result = await self.invoke(graph, request)
        logger.info(result)
        return None
