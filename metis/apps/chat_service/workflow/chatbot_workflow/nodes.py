from typing import Callable

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI

from apps.chat_service.user_types.chatbot_workflow import ChatBotWorkflowRequest
from apps.chat_service.workflow.chatbot_workflow.state import ChatBotWorkflowState


def add_workflow_request(request: ChatBotWorkflowRequest) -> Callable:
    def execute(state: ChatBotWorkflowState) -> ChatBotWorkflowState:
        state["workflow_request"] = request
        return state

    return execute


def add_prompt_message(state: ChatBotWorkflowState) -> ChatBotWorkflowState:
    if state["workflow_request"].system_message_prompt:
        state["messages"].append(
            SystemMessage(content=state["workflow_request"].system_message_prompt)
        )
    return state


def add_rag_message(state: ChatBotWorkflowState) -> ChatBotWorkflowState:
    if state["workflow_request"].rag_context:
        state["messages"].append(HumanMessage(
            content=state["workflow_request"].rag_context)
        )
    return state


def add_chat_history(state: ChatBotWorkflowState) -> ChatBotWorkflowState:
    if state['workflow_request'].chat_history:
        for history in state['workflow_request'].chat_history:
            if history.event == "user":
                human_msg = [{
                    "type": "text",
                    "text": history.text
                }]
                if history.image_data:
                    human_msg.append({
                        "type": "image_url",
                        "image_url": {
                            "url": history.image_data,
                            "detail": "auto"
                        }
                    })
                state["messages"].append(HumanMessage(human_msg))
            if history.event == "bot":
                bot_msg = [{
                    "type": "text",
                    "text": history.text
                }]
                state["messages"].append(HumanMessage(bot_msg))


def chatbot(request: ChatBotWorkflowRequest):
    llm = ChatOpenAI(model=request.model, base_url=request.openai_api_base,
                     api_key=request.openai_api_key, temperature=request.temperature)

    def execute(state: ChatBotWorkflowState) -> ChatBotWorkflowState:
        message = state["messages"]
        message.append(request.user_message)
        return {
            "messages": [
                llm.invoke(message)
            ]}

    return execute
