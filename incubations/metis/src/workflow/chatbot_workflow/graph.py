import os

from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.constants import END
from langgraph.graph import StateGraph

from src.core.graph import BasicGraph
from src.workflow.chatbot_workflow.entity import ChatBotWorkflowRequest, ChatBotWorkflowResponse
from src.workflow.chatbot_workflow.nodes import ChatBotWorkflowNode
from src.workflow.chatbot_workflow.state import ChatBotWorkflowState


class ChatBotWorkflowGraph(BasicGraph):
    def __init__(self, request: ChatBotWorkflowRequest):
        super().__init__(request)
        self.node_builder = ChatBotWorkflowNode(self.request)
        self.graph_builder = StateGraph(ChatBotWorkflowState)

    def compile_graph(self):
        last_edge = self.prepare_graph()
        self.graph_builder.add_node("chatbot_node", self.node_builder.chatbot_node)

        self.graph_builder.add_edge(last_edge, "chatbot_node")
        self.graph_builder.add_edge("chatbot_node", END)

        graph = self.graph_builder.compile()
        self.graph = graph

    def execute(self) -> ChatBotWorkflowResponse:
        result = self.invoke()
        response = self.parse_basic_response(result)
        return response
