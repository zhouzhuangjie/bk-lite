import logging
from typing import TypedDict

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel

from src.rag.naive_rag.rag import ElasticSearchRag

logger = logging.getLogger(__name__)


class BasicNodes:
    def __init__(self, request: BaseModel) -> None:
        self.request = request

    def get_llm_client(self) -> ChatOpenAI:
        llm = ChatOpenAI(model=self.request.model, base_url=self.request.openai_api_base,
                         api_key=self.request.openai_api_key, temperature=self.request.temperature)
        return llm

    def init_request_node(self, state: TypedDict) -> TypedDict:
        return {
            "graph_request": self.request
        }

    def prompt_message_node(self, state: TypedDict) -> TypedDict:
        if state["graph_request"].system_message_prompt:
            state["messages"].append(
                SystemMessage(content=state["graph_request"].system_message_prompt)
            )
        return state

    def add_chat_history_node(self, state: TypedDict) -> TypedDict:
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

    def naive_rag_node(self, state: TypedDict) -> TypedDict:
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
        return state

    def user_message_node(self, state: TypedDict) -> TypedDict:
        state["messages"].append(HumanMessage(content=state["graph_request"].user_message))
        return state

    def chatbot_node(self, state: TypedDict) -> TypedDict:
        message = state["messages"]
        message.append(self.request.user_message)
        llm = self.get_llm_client()
        return {
            "messages": [
                llm.invoke(message)
            ]
        }

        return execute


class McpNodes(BasicNodes):
    def __init__(self, request: BaseModel) -> None:
        super().__init__(request)
        self.tools = []
        self.mcp_client = None
        # 初始化MCP客户端配置
        if self.request.mcp_servers:
            self.mcp_config = {
                server.name: {
                    "url": server.url,
                    "transport": 'sse'
                } for server in self.request.mcp_servers
            }
        else:
            self.mcp_config = {}

    async def cleanup(self):
        if self.mcp_client:
            try:
                await self.mcp_client.__aexit__(None, None, None)
            except Exception as e:
                pass

    async def agent_node(self, state: TypedDict) -> TypedDict:
        """
        使用LangGraph推荐方式实现的代理节点
        这个方法接收当前状态，使用LLM生成可能包含工具调用的回复
        """
        # 获取完整的消息历史
        messages = state["messages"]

        # 检查最后一条消息，如果是工具消息并且有错误，记录日志
        if messages and isinstance(messages[-1], ToolMessage) and messages[-1].status == 'error':
            logger.warning(f"Tool execution error: {messages[-1].content}")

        try:
            # 确保工具已加载
            if not self.tools and self.request.mcp_servers:
                if not self.mcp_client:
                    # 如果客户端还没初始化，初始化它
                    self.mcp_client = MultiServerMCPClient(self.mcp_config)
                    await self.mcp_client.__aenter__()

                self.tools = self.mcp_client.get_tools()

            # 创建一个绑定了工具的LLM
            llm = self.get_llm_client()
            llm_with_tools = llm.bind_tools(self.tools)

            # 调用LLM生成回复（可能包含工具调用）
            response = await llm_with_tools.ainvoke(messages)

            # 更新消息列表
            state["messages"].append(response)

            # 如果需要，更新agent_scratchpad字段
            if "agent_scratchpad" in state:
                state["agent_scratchpad"] = response.content

            return state
        except Exception as e:
            logger.error(f"Error in agent_node: {e}")
            # 在出错的情况下，添加一个错误消息
            state["messages"].append(AIMessage(content=f"抱歉，处理您的请求时遇到了技术问题: {str(e)}"))
            return state

    async def build_tools_node(self) -> ToolNode:
        if self.request.mcp_servers:
            try:
                # 使用上下文管理器创建客户端
                self.mcp_client = MultiServerMCPClient(self.mcp_config)
                await self.mcp_client.__aenter__()  # 手动打开连接

                # 获取工具
                tools = self.mcp_client.get_tools()
                self.tools = tools

                # 创建工具节点，添加错误处理
                tool_node = ToolNode(tools, handle_tool_errors=True)

                return tool_node
            except Exception as e:
                self.tools = []
                return ToolNode([])
        else:
            return ToolNode([])
