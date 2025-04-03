import os
import traceback

from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.constants import START, END
from langgraph.graph import MessagesState

from src.core.entity import BasicLLMResponse, BasicLLMReuqest


class BasicGraph:

    def prepare_graph(self, graph_builder, node_builder) -> str:
        graph_builder.add_node("prompt_message_node", node_builder.prompt_message_node)
        graph_builder.add_node("add_chat_history_node", node_builder.add_chat_history_node)
        graph_builder.add_node("naive_rag_node", node_builder.naive_rag_node)
        graph_builder.add_node("user_message_node", node_builder.user_message_node)

        graph_builder.add_edge(START, "prompt_message_node")
        graph_builder.add_edge("prompt_message_node", "add_chat_history_node")
        graph_builder.add_edge("add_chat_history_node", "naive_rag_node")
        graph_builder.add_edge("naive_rag_node", "user_message_node")

        return 'user_message_node'

    def invoke(self, graph, request: BasicLLMReuqest):
        config = {
            "graph_request": request
        }

        if request.thread_id:
            config['configurable'] = {
                "thread_id": request.thread_id,
                "user_id": request.user_id
            }
            with PostgresSaver.from_conn_string(os.getenv('DB_URI')) as checkpoint:
                graph.checkpoint = checkpoint

        result = graph.invoke(request, config)
        return result

    def parse_basic_response(self, result):
        response = BasicLLMResponse(message=result["messages"][-1].content,
                                    total_tokens=result["messages"][-1].response_metadata['token_usage'][
                                        'total_tokens'])
        return response


class McpGraph(BasicGraph):

    def should_continue(self, state: MessagesState):
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools"
        return END

    async def invoke(self, graph, request: BasicLLMReuqest):
        config = {
            "graph_request": request
        }

        try:
            if request.thread_id:
                config['configurable'] = {
                    "thread_id": request.thread_id,
                    "user_id": request.user_id
                }
                with PostgresSaver.from_conn_string(os.getenv('DB_URI')) as checkpoint:
                    graph.checkpoint = checkpoint

            result = await graph.ainvoke(request, config)
            return result
        except Exception as e:
            print(traceback.format_exc())
            return None
