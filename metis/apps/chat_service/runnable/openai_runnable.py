from typing import AsyncIterator, Dict, Any, TYPE_CHECKING
from langchain_core.runnables import RunnableLambda
import json

from langserve import add_routes
from loguru import logger

from apps.chat_service.driver.openai_driver import OpenAIDriver
from apps.chat_service.user_types.openai_chat_request import OpenAIChatRequest


class OpenAIRunnable:
    """
    OpenAI 可运行服务类，提供聊天服务的路由和处理功能
    
    负责处理常规聊天请求和流式聊天请求，并将这些请求路由到相应的处理函数
    """

    def __init__(self):
        """初始化 OpenAIRunnable 实例"""
        logger.info("初始化 OpenAI 可运行服务")

    def _create_driver(self, req: OpenAIChatRequest, streaming: bool = False) -> OpenAIDriver:
        """
        创建 OpenAIDriver 实例
        
        Args:
            req: OpenAI 聊天请求对象
            streaming: 是否为流式请求
            
        Returns:
            已配置的 OpenAIDriver 实例
        """
        driver_type = OpenAIDriver.TYPE_STREAMING if streaming else OpenAIDriver.TYPE_NORMAL
        
        return OpenAIDriver.create(
            openai_api_key=req.openai_api_key,
            openai_base_url=req.openai_api_base,
            temperature=req.temperature,
            model=req.model,
            driver_type=driver_type
        )

    def _prepare_chat_params(self, req: OpenAIChatRequest, driver: OpenAIDriver) -> Dict[str, Any]:
        """
        准备聊天所需的参数
        
        Args:
            req: OpenAI 聊天请求对象
            driver: 已初始化的 OpenAIDriver 实例
            
        Returns:
            聊天参数字典
        """
        # 构建聊天历史
        llm_chat_history = driver.build_chat_history(
            req.chat_history,
            req.conversation_window_size
        )

        # 返回所有聊天参数
        return {
            "system_prompt": req.system_message_prompt,
            "user_message": req.user_message,
            "message_history": llm_chat_history,
            "rag_content": req.rag_context,
            "mcp_servers": req.mcp_servers,
            "trace_id": req.trace_id,
            "image_data": req.image_data,
        }

    async def openai_chat(self, req: OpenAIChatRequest) -> str:
        """
        处理常规聊天请求
        
        Args:
            req: OpenAI 聊天请求对象
            
        Returns:
            聊天响应结果的 JSON 字符串
        """
        logger.debug(f"接收聊天请求: {req.user_message[:100]}...")

        # 创建常规驱动和准备参数
        driver = self._create_driver(req, streaming=False)
        chat_params = self._prepare_chat_params(req, driver)

        # 执行聊天并返回结果
        result = await driver.chat_with_history(**chat_params)

        return result

    async def stream_chat(self, req: OpenAIChatRequest) -> AsyncIterator[str]:
        """
        处理流式聊天请求
        
        Args:
            req: OpenAI 聊天请求对象
            
        Returns:
            流式聊天响应的异步迭代器，每个响应都是 JSON 字符串
        """
        logger.info(f"接收流式聊天请求: {req.user_message[:100]}...")

        # 创建流式驱动和准备参数
        driver = self._create_driver(req, streaming=True)
        chat_params = self._prepare_chat_params(req, driver)

        # 执行流式聊天并返回结果
        async for chunk in driver.stream_chat_with_history(**chat_params):
            # 将字典格式的块转换为与 openai_chat 相同格式的 JSON 字符串
            response = {
                "result": True,
                "data": {
                    "content": chunk.get("content", ""),
                    "input_tokens": chunk.get("input_tokens", 0),
                    "output_tokens": chunk.get("output_tokens", 0),
                    "done": chunk.get("done", False)
                }
            }
            # 如果有错误信息，添加到响应中
            if "error" in chunk:
                response["data"]["error"] = chunk["error"]
            
            # 如果有类型信息，添加到响应中
            if "type" in chunk:
                response["data"]["type"] = chunk["type"]
                
            yield json.dumps(response, ensure_ascii=False)

    def register(self, app):
        """
        注册 API 路由
        
        Args:
            app: FastAPI 应用实例
        """
        logger.info("注册 OpenAI 聊天服务路由")

        # 添加常规聊天路由
        add_routes(
            app,
            RunnableLambda(self.openai_chat).with_types(
                input_type=OpenAIChatRequest,
                output_type=str
            ),
            path='/openai'
        )

        # 添加流式聊天路由
        add_routes(
            app,
            RunnableLambda(self.stream_chat),
            path='/openai/stream'
        )
