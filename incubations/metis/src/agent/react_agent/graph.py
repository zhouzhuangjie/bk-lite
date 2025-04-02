import os

from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode

from src.agent.tools_agent.entity import ToolsAgentRequest, ToolsAgentResponse
from src.agent.tools_agent.nodes import ToolsAgentNode
from src.agent.tools_agent.state import ToolsAgentState
from langchain_mcp_adapters.client import MultiServerMCPClient


class ToolsAgentGraph:

    def __init__(self, request: ToolsAgentRequest):
        self.request = request

    async def compile_graph(self):
        mcp_config = {
            server.name: {
                "url": server.url,
                "transport": 'sse'
            } for server in self.request.mcp_servers
        }

        async with MultiServerMCPClient(mcp_config) as mcp_server:
            node_builder = ToolsAgentNode(self.request)
            graph_builder = StateGraph(ToolsAgentState)
            graph_builder.add_node("init_request_node", node_builder.init_request_node)
            graph_builder.add_node("prompt_message_node", node_builder.prompt_message_node)
            graph_builder.add_node("add_chat_history_node", node_builder.add_chat_history_node)
            graph_builder.add_node("naive_rag_node", node_builder.naive_rag_node)

            tools = mcp_server.get_tools()
            tool_node = ToolNode(tools)
            graph_builder.add_node("tools", tool_node)
            graph_builder.add_edge(START, "init_request_node")
            graph_builder.add_edge("init_request_node", "prompt_message_node")
            graph_builder.add_edge("prompt_message_node", "add_chat_history_node")
            graph_builder.add_edge("add_chat_history_node", "naive_rag_node")
            graph_builder.add_edge("naive_rag_node", "chatbot_node")
            graph_builder.add_edge("chatbot_node", END)

            graph = graph_builder.compile()
            self.graph = graph

    def invoke(self) -> ToolsAgentResponse:
        if self.request.thread_id:
            config = {
                "configurable":
                    {
                        "thread_id": self.request.thread_id,
                        "user_id": self.request.user_id
                    }
            }
            with PostgresSaver.from_conn_string(os.getenv('DB_URI')) as checkpoint:
                self.graph.checkpoint = checkpoint
                result = self.graph.invoke(self.request, config)
        else:
            result = self.graph.invoke(self.request)

        response = ToolsAgentResponse(message=result["messages"][-1].content,
                                      total_tokens=result["messages"][-1].response_metadata['token_usage'][
                                          'total_tokens'])
        return response
