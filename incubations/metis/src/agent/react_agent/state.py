from typing import TypedDict, Annotated

from langgraph.graph import add_messages

from src.agent.tools_agent.entity import ToolsAgentRequest


class ToolsAgentState(TypedDict):
    messages: Annotated[list, add_messages]
    graph_request: ToolsAgentRequest
