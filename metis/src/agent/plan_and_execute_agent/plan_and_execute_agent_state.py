import operator
from typing import TypedDict, Annotated, List, Tuple

from langgraph.graph import add_messages
from pydantic import Field

from src.entity.agent.plan_and_execute_agent_request import PlanAndExecuteAgentRequest


class PlanAndExecuteAgentState(TypedDict):
    messages: Annotated[list, add_messages]
    graph_request: PlanAndExecuteAgentRequest
    plan: List[str] = Field(
        description="different steps to follow, should be in sorted order"
    )
    past_steps: Annotated[List[Tuple], operator.add]
    response: str
