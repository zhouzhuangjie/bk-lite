from typing import TypedDict, Annotated

from langgraph.graph import add_messages

from src.workflow.chatbot_workflow.entity import ChatBotWorkflowRequest


class ChatBotWorkflowState(TypedDict):
    messages: Annotated[list, add_messages]
    graph_request: ChatBotWorkflowRequest
