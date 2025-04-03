import logging
from typing import TypedDict

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel

from src.core.entity import BasicLLMReuqest
from src.rag.naive_rag.rag import ElasticSearchRag

logger = logging.getLogger(__name__)


class BasicNodes:

    def get_llm_client(self, request: BasicLLMReuqest) -> ChatOpenAI:
        llm = ChatOpenAI(model=request.model, base_url=request.openai_api_base,
                         api_key=request.openai_api_key, temperature=request.temperature)
        return llm

    def prompt_message_node(self, state: TypedDict, config: RunnableConfig) -> TypedDict:
        if config["configurable"]["graph_request"].system_message_prompt:
            state["messages"].append(
                SystemMessage(content=config["configurable"]["graph_request"].system_message_prompt)
            )
        return state

    def add_chat_history_node(self, state: TypedDict, config: RunnableConfig) -> TypedDict:
        if config["configurable"]['graph_request'].chat_history:
            for chat in config["configurable"]['graph_request'].chat_history:
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

    def naive_rag_node(self, state: TypedDict, config: RunnableConfig) -> TypedDict:
        if config["configurable"]['graph_request'].enable_naive_rag is False:
            return state

        naive_rag_request = config["configurable"]["graph_request"].naive_rag_request
        elasticsearch_rag = ElasticSearchRag()
        rag_result = elasticsearch_rag.search(naive_rag_request)

        rag_message = "以下是提供给你参考的背景信息：\n"
        for r in rag_result:
            rag_message += f"""
                Title: {r.metadata['_source']['metadata']['knowledge_title']}
                Chunk: {r.page_content}
            """
        state["messages"].append(HumanMessage(content=rag_message))
        return state

    def user_message_node(self, state: TypedDict, config: RunnableConfig) -> TypedDict:
        state["messages"].append(HumanMessage(content=config["configurable"]["graph_request"].user_message))
        return state

    def chatbot_node(self, state: TypedDict, config: RunnableConfig) -> TypedDict:
        message = state["messages"]
        message.append(config["configurable"]["graph_request"].user_message)
        llm = self.get_llm_client(config["configurable"]["graph_request"])
        return {
            "messages": [
                llm.invoke(message)
            ]
        }

        return execute


class McpNodes(BasicNodes):
    def __init__(self) -> None:
        self.tools = []
        self.mcp_client = None

    async def setup(self, request: BaseModel):
        # 初始化MCP客户端配置
        if request.mcp_servers:
            self.mcp_config = {
                server.name: {
                    "url": server.url,
                    "transport": 'sse'
                } for server in request.mcp_servers
            }
        else:
            self.mcp_config = {}
        self.mcp_client = MultiServerMCPClient(self.mcp_config)
        await self.mcp_client.__aenter__()  # 手动打开连接
        self.tools = self.mcp_client.get_tools()

    async def agent_node(self, state: TypedDict, config: RunnableConfig) -> TypedDict:
        # 获取完整的消息历史
        messages = state["messages"]

        # 检查最后一条消息，如果是工具消息并且有错误，记录日志
        if messages and isinstance(messages[-1], ToolMessage) and messages[-1].status == 'error':
            logger.warning(f"Tool execution error: {messages[-1].content}")

        # 创建一个绑定了工具的LLM
        llm = self.get_llm_client(config["configurable"]["graph_request"])
        llm_with_tools = llm.bind_tools(self.tools)

        # 调用LLM生成回复（可能包含工具调用）
        response = await llm_with_tools.ainvoke(messages)

        # 更新消息列表
        state["messages"].append(response)

        return state

    async def build_tools_node(self) -> ToolNode:
        if self.tools:
            try:
                tool_node = ToolNode(self.tools, handle_tool_errors=True)
                return tool_node
            except Exception as e:
                self.tools = []
                return ToolNode([])
        else:
            return ToolNode([])
