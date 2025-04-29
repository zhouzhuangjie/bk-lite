import os

from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.constants import START

from src.core.entity.basic_llm_request import BasicLLMReuqest
from src.core.entity.basic_llm_response import BasicLLMResponse


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
            "graph_request": request,
            "recursion_limit": 10,
            "configurable": {
                **request.extra_config,
            }
        }

        if request.thread_id:
            config['configurable'] = {
                "thread_id": request.thread_id,
                "user_id": request.user_id,
                **(config['configurable'] or {})
            }
            with PostgresSaver.from_conn_string(os.getenv('DB_URI')) as checkpoint:
                graph.checkpoint = checkpoint

        result = graph.invoke(request, config)
        return result

