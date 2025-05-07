from typing import TypedDict

from langchain_core.runnables import RunnableConfig

from src.core.node.basic_node import BasicNode


class ChatBotWorkflowNode(BasicNode):
    def chatbot_node(self, state: TypedDict, config: RunnableConfig) -> TypedDict:
        message = state["messages"]
        message.append(config["configurable"]["graph_request"].user_message)
        llm = self.get_llm_client(config["configurable"]["graph_request"])
        message = llm.invoke(message)
        return {
            "messages": [message]
        }
