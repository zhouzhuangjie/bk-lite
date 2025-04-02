from typing import TypedDict, Annotated

from langgraph.graph import add_messages

from src.agent.react_agent.entity import ReActAgentRequest


class ReActAgentState(TypedDict):
    messages: Annotated[list, add_messages]
    graph_request: ReActAgentRequest
    agent_scratchpad: str
