import os

from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.constants import END
from langgraph.graph import StateGraph

from src.core.graph import BasicGraph
from src.workflow.chatbot_workflow.entity import ChatBotWorkflowRequest, ChatBotWorkflowResponse
from src.workflow.chatbot_workflow.nodes import ChatBotWorkflowNode
from src.workflow.chatbot_workflow.state import ChatBotWorkflowState


class ChatBotWorkflowGraph(BasicGraph):

    def compile_graph(self, request: ChatBotWorkflowRequest):
        graph_builder = StateGraph(ChatBotWorkflowState)
        node_builder = ChatBotWorkflowNode()

        last_edge = self.prepare_graph(graph_builder,node_builder)
        graph_builder.add_node("chatbot_node", node_builder.chatbot_node)

        graph_builder.add_edge(last_edge, "chatbot_node")
        graph_builder.add_edge("chatbot_node", END)

        graph = graph_builder.compile()
        return graph

    def execute(self, request: ChatBotWorkflowRequest) -> ChatBotWorkflowResponse:
        graph = self.compile_graph(request)
        result = self.invoke(graph, request)
        response = self.parse_basic_response(result)
        return response
