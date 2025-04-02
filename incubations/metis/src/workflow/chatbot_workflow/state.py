from src.core.state import BasicState
from src.workflow.chatbot_workflow.entity import ChatBotWorkflowRequest


class ChatBotWorkflowState(BasicState):
    graph_request: ChatBotWorkflowRequest
