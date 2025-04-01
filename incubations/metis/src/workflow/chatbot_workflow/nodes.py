from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

from src.workflow.chatbot_workflow.entity import ChatBotWorkflowRequest
from src.workflow.chatbot_workflow.state import ChatBotWorkflowState


class ChatBotWorkflowNode:
    def __init__(self, request: ChatBotWorkflowRequest) -> None:
        self.request = request
        self.llm = ChatOpenAI(model=self.request.model, base_url=self.request.openai_api_base,
                              api_key=self.request.openai_api_key, temperature=self.request.temperature)

    def init_request_node(self, state: ChatBotWorkflowState) -> ChatBotWorkflowState:
        return {
            "workflow_request": self.request
        }

    def prompt_message_node(self, state: ChatBotWorkflowState) -> ChatBotWorkflowState:
        if state["workflow_request"].system_message_prompt:
            state["messages"].append(
                SystemMessage(content=state["workflow_request"].system_message_prompt)
            )
        return state

    def chatbot_node(self, state: ChatBotWorkflowState) -> ChatBotWorkflowState:
        message = state["messages"]
        message.append(self.request.user_message)
        return {
            "messages": [
                self.llm.invoke(message)
            ]}

        return execute
