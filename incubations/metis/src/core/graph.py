import os
import traceback
from typing import TypedDict

from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph, MessagesState

from src.core.entity import BasicLLMReuqest, BasicLLMResponse
from src.core.nodes import BasicNodes


class BasicGraph:
    def __init__(self, request: BasicLLMReuqest):
        self.request = request
        self.graph = None
        self.node_builder = None

    def prepare_graph(self) -> str:

        self.graph_builder.add_node("init_request_node", self.node_builder.init_request_node)
        self.graph_builder.add_node("prompt_message_node", self.node_builder.prompt_message_node)
        self.graph_builder.add_node("add_chat_history_node", self.node_builder.add_chat_history_node)
        self.graph_builder.add_node("naive_rag_node", self.node_builder.naive_rag_node)
        self.graph_builder.add_node("user_message_node", self.node_builder.user_message_node)

        self.graph_builder.add_edge(START, "init_request_node")
        self.graph_builder.add_edge("init_request_node", "prompt_message_node")
        self.graph_builder.add_edge("prompt_message_node", "add_chat_history_node")
        self.graph_builder.add_edge("add_chat_history_node", "naive_rag_node")
        self.graph_builder.add_edge("naive_rag_node", "user_message_node")

        return 'user_message_node'

    def invoke(self):
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
        return result

    def parse_basic_response(self, result):
        response = BasicLLMResponse(message=result["messages"][-1].content,
                                    total_tokens=result["messages"][-1].response_metadata['token_usage'][
                                        'total_tokens'])
        return response


class McpGraph(BasicGraph):
    def __init__(self, request: BasicLLMReuqest):
        super().__init__(request)

    def should_continue(self, state: MessagesState):
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools"
        return END

    async def invoke(self):
        try:
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
                    result = await self.graph.ainvoke(self.request, config)
            else:
                result = await self.graph.ainvoke(self.request)
            return result
        except Exception as e:
            print(traceback.format_exc())
        finally:
            if self.node_builder and hasattr(self.node_builder, "cleanup"):
                await self.node_builder.cleanup()
        return None
