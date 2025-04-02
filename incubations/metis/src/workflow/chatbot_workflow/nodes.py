from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

from src.rag.naive_rag.rag import ElasticSearchRag
from src.workflow.chatbot_workflow.entity import ChatBotWorkflowRequest
from src.workflow.chatbot_workflow.state import ChatBotWorkflowState


class ChatBotWorkflowNode:
    def __init__(self, request: ChatBotWorkflowRequest) -> None:
        self.request = request
        self.llm = ChatOpenAI(model=self.request.model, base_url=self.request.openai_api_base,
                              api_key=self.request.openai_api_key, temperature=self.request.temperature)

    def init_request_node(self, state: ChatBotWorkflowState) -> ChatBotWorkflowState:
        return {
            "graph_request": self.request
        }

    def prompt_message_node(self, state: ChatBotWorkflowState) -> ChatBotWorkflowState:
        if state["graph_request"].system_message_prompt:
            state["messages"].append(
                SystemMessage(content=state["graph_request"].system_message_prompt)
            )
        return state

    def add_chat_history_node(self, state: ChatBotWorkflowState) -> ChatBotWorkflowState:
        if state['graph_request'].chat_history:
            for chat in state['graph_request'].chat_history:
                if chat.event == 'user':
                    if chat.image_data:
                        state['messages'].append(HumanMessage(content=[
                            {"type": "text", "text": "describe the weather in this image"},
                            {"type": "image_url", "image_url": {"url": chat.image_data}},
                        ]))
                    else:
                        state['messages'].append(HumanMessage(content=chat.message))
                elif chat.event == 'assistant':
                    state['messages'].append(AIMessage(content=chat.message))
        return state

    def naive_rag_node(self, state: ChatBotWorkflowState) -> ChatBotWorkflowState:
        if state['graph_request'].enable_naive_rag is False:
            return state

        naive_rag_request = state["graph_request"].naive_rag_request
        elasticsearch_rag = ElasticSearchRag()
        rag_result = elasticsearch_rag.search(naive_rag_request)

        rag_message = "以下是提供给你参考的背景信息：\n"
        for r in rag_result:
            rag_message += f"""
                Title: {r.metadata['_source']['metadata']['knowledge_title']}
                Chunk: {r.page_content}
            """
        state["messages"].append(HumanMessage(content=rag_message))
        print(rag_message)
        return state

    def chatbot_node(self, state: ChatBotWorkflowState) -> ChatBotWorkflowState:
        message = state["messages"]
        message.append(self.request.user_message)
        return {
            "messages": [
                self.llm.invoke(message)
            ]}

        return execute
