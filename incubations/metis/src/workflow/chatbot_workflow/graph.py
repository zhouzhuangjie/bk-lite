import os

from langgraph.constants import START, END
from langgraph.graph import StateGraph

from src.workflow.chatbot_workflow.entity import ChatBotWorkflowRequest
from src.workflow.chatbot_workflow.nodes import ChatBotWorkflowNode
from src.workflow.chatbot_workflow.state import ChatBotWorkflowState
from langgraph.checkpoint.postgres import PostgresSaver


class ChatBotWorkflowGraph:
    def __init__(self, request: ChatBotWorkflowRequest, checkpoint: PostgresSaver):
        self.checkpoint = checkpoint
        self.request = request

    def build_graph(self) -> StateGraph:
        node_builder = ChatBotWorkflowNode(self.request)
        graph_builder = StateGraph(ChatBotWorkflowState)
        graph_builder.add_node("init_request_node", node_builder.init_request_node)
        graph_builder.add_node("prompt_message_node", node_builder.prompt_message_node)
        graph_builder.add_node("chatbot_node", node_builder.chatbot_node)

        graph_builder.add_edge(START, "init_request_node")
        graph_builder.add_edge("init_request_node", "prompt_message_node")
        graph_builder.add_edge("prompt_message_node", "chatbot_node")
        graph_builder.add_edge("chatbot_node", END)

        graph = graph_builder.compile(checkpointer=self.checkpoint)
        return graph
