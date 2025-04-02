import os
from typing import Annotated, AsyncIterator

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.graph.state import CompiledStateGraph
from typing_extensions import TypedDict

from apps.chat_service.user_types.chatbot_workflow import ChatBotWorkflowRequest, ChatBotWorkflowResponse


class State(TypedDict):
    messages: Annotated[list, add_messages]


class ChatBotWorkflow:
    def build_graph(self, request: ChatBotWorkflowRequest) -> CompiledStateGraph:

        def chatbot(state: State):
            message = []

            if request.system_message_prompt:
                message.append(SystemMessage(content=request.system_message_prompt))

            if request.rag_context:
                message.append(HumanMessage(content=f"""
                    以下是参考信息：
                        {request.rag_context}
                """))

            if request.chat_history:
                for history in request.chat_history:
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
                        message.append(HumanMessage(human_msg))
                    if history.event == "bot":
                        bot_msg = [{
                            "type": "text",
                            "text": history.text
                        }]
                        message.append(AIMessage(bot_msg))
            for msg in state["messages"]:
                message.append(msg)

            return {"messages": [
                llm.invoke(message)
            ]}

        llm = ChatOpenAI(model=request.model, base_url=request.openai_api_base,
                         api_key=request.openai_api_key, temperature=request.temperature)
        graph_builder = StateGraph(State)
        graph_builder.add_node("chatbot", chatbot)
        graph_builder.add_edge(START, "chatbot")
        graph_builder.add_edge("chatbot", END)
        graph = graph_builder.compile()
        return graph

    def invoke(self, request: ChatBotWorkflowRequest) -> ChatBotWorkflowResponse:
        graph = self.build_graph(request)
        result = graph.invoke({"messages": request.user_message})
        response = ChatBotWorkflowResponse(
            message=result['messages'][-1].content,
            total_tokens=result['messages'][-1].response_metadata['token_usage']['total_tokens'],
        )
        return response
