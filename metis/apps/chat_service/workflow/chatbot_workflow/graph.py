from langgraph.constants import START, END
from langgraph.graph import StateGraph

from apps.chat_service.workflow.chatbot_workflow.nodes import add_workflow_request, add_prompt_message, add_rag_message, \
    add_chat_history, chatbot
from apps.chat_service.workflow.chatbot_workflow.state import ChatBotWorkflowState


def chatbot_workflow(request: ChatBotWorkflowState):
    graph_builder = StateGraph(ChatBotWorkflowState)

    init_request = add_workflow_request(request)
    graph_builder.add_node('add_workflow_request', init_request)
    graph_builder.add_node('add_prompt_message', add_prompt_message)
    graph_builder.add_node('add_rag_message', add_rag_message)
    graph_builder.add_node('add_chat_history', add_chat_history)

    bot = chatbot(request)
    graph_builder.add_node("chatbot", bot)

    graph_builder.add_edge(START, "add_workflow_request")
    graph_builder.add_edge('add_workflow_request', "add_prompt_message")
    graph_builder.add_edge('add_prompt_message', "add_rag_message")
    graph_builder.add_edge('add_rag_message', "add_chat_history")
    graph_builder.add_edge('add_chat_history', "chatbot")
    graph_builder.add_edge("chatbot", END)

    graph = graph_builder.compile()
    return graph
