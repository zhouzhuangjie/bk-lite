from typing import Annotated, TypedDict

from langgraph.graph import add_messages

from apps.chat_service.user_types.chatbot_workflow import ChatBotWorkflowRequest


class ChatBotWorkflowState(TypedDict):
    messages: Annotated[list, add_messages]
    workflow_request: ChatBotWorkflowRequest
