import os

from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph

from src.agent.react_agent.entity import ReActAgentRequest, ReActAgentResponse
from src.agent.react_agent.nodes import ReActAgentNode
from src.agent.react_agent.state import ReActAgentState
from src.core.graph import McpGraph


class ReActAgentGraph(McpGraph):
    def __init__(self, request: ReActAgentRequest):
        super().__init__(request)
        self.node_builder = ReActAgentNode(self.request)
        self.graph_builder = StateGraph(ReActAgentState)

    async def compile_graph(self):
        last_edge = self.prepare_graph()

        tools_node = await self.node_builder.build_tools_node()
        self.graph_builder.add_node("tools", tools_node)
        self.graph_builder.add_node("agent", self.node_builder.agent_node)

        self.graph_builder.add_edge(last_edge, "agent")
        self.graph_builder.add_conditional_edges("agent", self.should_continue, ["tools", END])
        self.graph_builder.add_edge("tools", "agent")

        self.graph = self.graph_builder.compile()

    async def execute(self) -> ReActAgentResponse:
        result = await self.invoke()
        response = self.parse_basic_response(result)
        return response
