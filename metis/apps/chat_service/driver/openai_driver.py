import json
import time
from typing import List, Any, Dict, Tuple, Union, Optional, AsyncIterator

from langchain.agents import initialize_agent, AgentType
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from loguru import logger
import tiktoken
from langchain_community.chat_message_histories import ChatMessageHistory

from apps.chat_service.user_types.chat_history import ChatHistory
from apps.chat_service.user_types.mcp_server import McpServer


class OpenAIDriver:
    """OpenAI 驱动类，处理与 OpenAI 模型的交互"""
    
    def __init__(self, openai_api_key: str, openai_base_url: str, temperature: float, model: str):
        """
        初始化 OpenAI 驱动
        
        Args:
            openai_api_key: OpenAI API 密钥
            openai_api_base: OpenAI API 基础 URL
            temperature: 温度参数，控制输出随机性
            model: 使用的模型名称
        """
        self.model = model
        self.common_params = {
            "openai_api_key": openai_api_key,
            "openai_api_base": openai_base_url,
            "temperature": temperature,
            "model": model,
            "max_retries": 3,
        }
        
        # 常规客户端
        self.client = ChatOpenAI(**self.common_params)
        
        # 流式响应客户端
        self.streaming_client = ChatOpenAI(**self.common_params, streaming=True)
        
        # 初始化分词器
        try:
            self.encoding = tiktoken.encoding_for_model(model)
        except Exception:
            logger.warning(f"无法找到模型 {model} 的分词器，使用默认分词器")
            self.encoding = tiktoken.get_encoding("cl100k_base")

    def build_chat_history(self, chat_history: List[ChatHistory], window_size: int) -> ChatMessageHistory:
        """
        构建 LLM 聊天历史
        
        Args:
            chat_history: 聊天历史列表
            window_size: 历史窗口大小
            
        Returns:
            构建好的 ChatMessageHistory 对象
        """
        llm_chat_history = ChatMessageHistory()

        if chat_history:
            for event in chat_history[-window_size:]:
                if event.text is None:
                    logger.debug(f"跳过无文本事件: {event}")
                    continue

                if event.event == "user":
                    llm_chat_history.add_user_message(event.text)
                elif event.event == "bot":
                    llm_chat_history.add_ai_message(event.text)

        return llm_chat_history

    def count_tokens(self, text: str) -> int:
        """
        计算文本的 token 数量
        
        Args:
            text: 要计算的文本
            
        Returns:
            token 数量
        """
        if not text:
            return 0
        return len(self.encoding.encode(text))

    def count_message_tokens(self, messages: List[Dict]) -> Tuple[int, int]:
        """
        计算消息列表的输入和输出 token 数量
        
        Args:
            messages: 消息列表
            
        Returns:
            (输入token数, 输出token数) 元组
        """
        input_tokens = output_tokens = 0

        for message in messages:
            content = message.content
            input_tokens += self.count_tokens(content)

        return input_tokens, output_tokens

    def create_prompt_template(self, system_content: str) -> ChatPromptTemplate:
        """
        创建对话提示模板
        
        Args:
            system_content: 系统提示内容
            
        Returns:
            ChatPromptTemplate 对象
        """
        return ChatPromptTemplate.from_messages([
            ("system", system_content),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
        ])

    def _format_multimodal_message(self, user_message: str, image_data: Optional[List[str]] = None) -> Union[str, List[Dict]]:
        """
        格式化多模态消息，支持文本和图片
        
        Args:
            user_message: 用户文本消息
            image_data: 图片的base64编码列表
            
        Returns:
            格式化后的消息内容
        """
        if not image_data:
            return user_message

        content = [{"type": "text", "text": user_message}]

        for img in image_data:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"{img}"
                }
            })

        return content

    def _prepare_system_content(self, system_prompt: str, rag_content: str) -> str:
        """
        准备系统内容
        
        Args:
            system_prompt: 系统提示
            rag_content: RAG 上下文内容
            
        Returns:
            格式化后的系统内容
        """
        # 处理可能包含格式化占位符的 rag_content
        safe_rag_content = rag_content.replace('{', '{{').replace('}', '}}')
        return f"{system_prompt}, Here is some context: {safe_rag_content}"

    def _handle_multimodal_input(self, system_content: str, user_message: str, 
                               message_history: Any, image_data: List[str], is_streaming: bool = False):
        """
        处理多模态输入
        
        Args:
            system_content: 系统内容
            user_message: 用户消息
            message_history: 消息历史
            image_data: 图片数据
            is_streaming: 是否使用流式响应
            
        Returns:
            多模态输入处理的准备信息
        """
        logger.info(f"处理多模态输入，包含 {len(image_data)} 张图片")
        formatted_content = self._format_multimodal_message(user_message, image_data)
        
        # 构建消息列表
        messages = [{"role": "system", "content": system_content}]
        
        # 添加历史消息
        if hasattr(message_history, "messages") and message_history.messages:
            messages.extend(message_history.messages)
        
        # 添加当前带图片的消息
        messages.append({"role": "user", "content": formatted_content})
        
        # 选择客户端
        client = self.streaming_client if is_streaming else self.client
        
        return {'messages': messages, 'client': client}

    def _handle_text_input(self, system_content: str, user_message: str, message_history: Any, is_streaming: bool = False):
        """
        处理纯文本输入
        
        Args:
            system_content: 系统内容
            user_message: 用户消息
            message_history: 消息历史
            is_streaming: 是否使用流式响应
            
        Returns:
            文本输入处理的准备信息
        """
        # 创建提示模板
        prompt = self.create_prompt_template(system_content)
        
        # 选择客户端
        client = self.streaming_client if is_streaming else self.client
        
        # 创建对话链
        chain = prompt | client
        
        # 添加历史记录
        chain_with_history = RunnableWithMessageHistory(
            chain,
            get_session_history=lambda: message_history,
            input_messages_key="input",
            history_messages_key="chat_history",
        )
        
        return {'chain': chain_with_history, 'input': {"input": user_message}}

    def _invoke_simple_chain(self, user_message: str, message_history: Any, 
                           system_prompt: str, rag_content: str, trace_id: str, 
                           image_data: List[str] = []):
        """
        调用简单对话链
        
        Args:
            user_message: 用户消息
            message_history: 消息历史
            system_prompt: 系统提示
            rag_content: RAG 上下文
            trace_id: 追踪 ID
            image_data: 图片数据
            
        Returns:
            LLM 响应结果
        """
        start_time = time.time()
        logger.info(f"问题[{trace_id}]: {user_message}")

        # 准备系统内容
        system_content = self._prepare_system_content(system_prompt, rag_content)
        
        # 计算输入 token
        input_tokens = self.count_tokens(system_content) + self.count_tokens(user_message)

        # 为历史消息计算 token
        if hasattr(message_history, "messages") and message_history.messages:
            hist_input, hist_output = self.count_message_tokens(message_history.messages)
            input_tokens += hist_input + hist_output

        # 根据输入类型选择处理方法
        if image_data:
            # 处理多模态输入
            mm_data = self._handle_multimodal_input(system_content, user_message, message_history, image_data)
            result = mm_data['client'].invoke(mm_data['messages'])
        else:
            # 处理纯文本输入
            text_data = self._handle_text_input(system_content, user_message, message_history)
            result = text_data['chain'].invoke(text_data['input'])

        # 计算输出 token
        output_tokens = self.count_tokens(result.content)

        # 记录用量数据
        result.usage_metadata = {
            'input_tokens': input_tokens,
            'output_tokens': output_tokens
        }

        # 计算并记录耗时
        duration = time.time() - start_time
        logger.info(f"耗时:[{duration:.4f}秒],回复[{trace_id}]: {result}")
        
        return result

    async def execute_with_tools(self, user_message: str, message_history: Any, 
                               system_prompt: str, rag_content: str, mcp_servers: List[McpServer]):
        """
        使用工具执行查询
        
        Args:
            user_message: 用户消息
            message_history: 消息历史
            system_prompt: 系统提示
            rag_content: RAG 上下文
            mcp_servers: MCP 服务器列表
            
        Returns:
            更新后的 RAG 内容和 token 用量信息
        """
        # 配置 MCP 客户端
        mcp_config = {
            server.name: {
                "url": server.url,
                "transport": 'sse'
            } for server in mcp_servers
        }

        total_prompt_tokens = total_completion_tokens = 0

        async with MultiServerMCPClient(mcp_config) as mcp_server:
            tools = mcp_server.get_tools()

            # 初始化代理执行器
            agent_executor = initialize_agent(
                tools=tools,
                llm=self.client,
                handle_parsing_errors=True,
                agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
                verbose=True,
                max_iterations=5,
                early_stopping_method="generate",
                return_intermediate_steps=False,
            )

            # 准备输入数据
            input_data = {
                "input": user_message,
                "chat_history": message_history.messages,
                "rag_content": rag_content,
                "tools": [tool.name for tool in tools],
                "system_prompt": system_prompt,
            }

            # 代理系统模板
            agent_system_template = """     
                {system_prompt}

                Here is our chat history:
                {chat_history}

                Here is some context: 
                {rag_content}      

                Answer the following questions as best you can. You have access to the following tools:
                {tools}

                Use the following format:
                Question: the input question you must answer
                Thought: you should always think about what to do
                Action: the action to take, should be one of [{tools}]
                Action Input: the input to the action
                Observation: the result of the action
                ... (this Thought/Action/Action Input/Observation can repeat N times)
                Thought: I now know the final answer
                Final Answer: the final answer to the original input question
                Begin!
                Question: {input}
                Thought:{agent_scratchpad}
            """
            
            # 计算输入token
            agent_prompt = ChatPromptTemplate.from_messages([
                ("system", agent_system_template),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ])
            formatted_prompt = agent_prompt.format(**input_data)
            logger.debug(f"Formatted Prompt:\n{formatted_prompt}")
            total_prompt_tokens = self.count_tokens(formatted_prompt)

            # 执行工具调用
            tools_response = await agent_executor.ainvoke(input_data)
            logger.info(f"工具执行结果:{tools_response}")

            # 处理工具执行结果
            thoughts_result = tools_response['output']
            updated_rag_content = rag_content + f"""
                <function_call_thought>
                    {thoughts_result}
                </function_call_thought>
                """
            total_completion_tokens = self.count_tokens(thoughts_result)

        return updated_rag_content, total_prompt_tokens, total_completion_tokens

    async def chat_with_history(self, system_prompt: str, user_message: str,
                              message_history: List[ChatHistory], rag_content: str = "",
                              mcp_servers: List[McpServer] = [], trace_id: str = '',
                              image_data: List[str] = []) -> str:
        """
        与历史记录进行对话
        
        Args:
            system_prompt: 系统提示
            user_message: 用户消息
            message_history: 消息历史
            rag_content: RAG 上下文
            mcp_servers: MCP 服务器列表
            trace_id: 追踪 ID
            image_data: 图片数据
            
        Returns:
            对话结果的 JSON 字符串
        """
        try:
            logger.info(f"System Prompt: {system_prompt}, User Message: {user_message}, mcp_servers:{mcp_servers}")
            if image_data:
                logger.info(f"检测到多模态输入，包含 {len(image_data)} 张图片")

            total_prompt_tokens = total_completion_tokens = 0

            # 如果有工具服务器，先执行工具调用
            if mcp_servers:
                rag_content, tool_prompt_tokens, tool_completion_tokens = await self.execute_with_tools(
                    user_message, message_history, system_prompt, rag_content, mcp_servers
                )
                total_prompt_tokens += tool_prompt_tokens
                total_completion_tokens += tool_completion_tokens

            # 获取最终结果
            simple_result = self._invoke_simple_chain(
                user_message, message_history, system_prompt, rag_content, trace_id, image_data
            )

            # 更新token计数
            total_prompt_tokens += simple_result.usage_metadata['input_tokens']
            total_completion_tokens += simple_result.usage_metadata['output_tokens']

            # 返回格式化结果
            return json.dumps({
                "result": True,
                "data": {
                    "content": simple_result.content,
                    "input_tokens": total_prompt_tokens,
                    "output_tokens": total_completion_tokens,
                }
            }, ensure_ascii=False, indent=4)

        except Exception as e:
            logger.exception(f"聊天执行过程中出错: {str(e)}")
            return json.dumps({
                "result": True,
                "data": {
                    "content": "非常抱歉,触发了智能体的拦截策略,不能回复您哦.....",
                    "input_tokens": 0,
                    "output_tokens": 0,
                }
            }, ensure_ascii=False, indent=4)

    async def _stream_invoke_simple_chain(self, user_message: str, message_history: Any,
                                        system_prompt: str, rag_content: str, trace_id: str,
                                        image_data: List[str] = []) -> AsyncIterator[Dict[str, Any]]:
        """
        流式方式调用简单对话链
        
        Args:
            user_message: 用户消息
            message_history: 消息历史
            system_prompt: 系统提示
            rag_content: RAG 上下文
            trace_id: 追踪 ID
            image_data: 图片数据
            
        Returns:
            异步迭代器，生成流式响应内容
        """
        start_time = time.time()
        logger.info(f"流式问题[{trace_id}]: {user_message}")

        # 准备系统内容
        system_content = self._prepare_system_content(system_prompt, rag_content)
        
        # 计算输入 token
        input_tokens = self.count_tokens(system_content) + self.count_tokens(user_message)

        # 为历史消息计算 token
        if hasattr(message_history, "messages") and message_history.messages:
            hist_input, hist_output = self.count_message_tokens(message_history.messages)
            input_tokens += hist_input + hist_output

        output_tokens = 0
        final_text = ""

        # 处理多模态输入
        if image_data:
            # 准备多模态请求
            mm_data = self._handle_multimodal_input(
                system_content, user_message, message_history, image_data, is_streaming=True
            )
            
            # 流式响应
            async for chunk in mm_data['client'].astream(mm_data['messages']):
                if chunk.content:
                    final_text += chunk.content
                    output_tokens = self.count_tokens(final_text)
                    yield {
                        "content": chunk.content,
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "done": False
                    }
        else:
            # 准备文本请求
            text_data = self._handle_text_input(
                system_content, user_message, message_history, is_streaming=True
            )
            
            # 流式响应
            async for chunk in text_data['chain'].astream(text_data['input']):
                if chunk.content:
                    final_text += chunk.content
                    output_tokens = self.count_tokens(final_text)
                    yield {
                        "content": chunk.content,
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "done": False
                    }

        # 计算并记录耗时
        duration = time.time() - start_time
        logger.info(f"流式耗时:[{duration:.4f}秒],完成回复[{trace_id}]")
        
        # 发送完成消息
        yield {
            "content": "",
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "done": True
        }

    async def stream_chat_with_history(self, system_prompt: str, user_message: str,
                                     message_history: List[ChatHistory], rag_content: str = "",
                                     mcp_servers: List[McpServer] = [], trace_id: str = '',
                                     image_data: List[str] = []) -> AsyncIterator[Dict[str, Any]]:
        """
        流式方式与历史对话
        
        Args:
            system_prompt: 系统提示
            user_message: 用户消息
            message_history: 消息历史
            rag_content: RAG 上下文
            mcp_servers: MCP 服务器列表
            trace_id: 追踪 ID
            image_data: 图片数据
            
        Returns:
            异步迭代器，生成流式响应内容
        """
        try:
            # 记录请求信息
            self._log_chat_request(user_message, system_prompt, image_data, trace_id, is_stream=True)
            
            # 初始化token计数
            total_prompt_tokens = 0

            # 执行工具调用（如果有）
            updated_rag, tool_tokens = await self._execute_tool_calls_if_needed(
                user_message, message_history, system_prompt, rag_content, mcp_servers
            )
            
            # 更新token计数和RAG内容
            if tool_tokens > 0:
                total_prompt_tokens += tool_tokens
                rag_content = updated_rag
                
                # 发送工具调用的通知
                yield self._create_tool_execution_chunk(total_prompt_tokens)

            # 流式获取最终结果
            async for chunk in self._stream_invoke_simple_chain(
                    user_message, message_history, system_prompt, rag_content, trace_id, image_data
            ):
                # 更新token计数
                chunk["input_tokens"] += total_prompt_tokens
                yield chunk

        except Exception as e:
            # 记录异常并返回友好错误消息
            error_msg = f"流式聊天处理异常: {str(e)}"
            logger.exception(error_msg)
            yield self._create_error_response_chunk(error_msg)
    
    def _log_chat_request(self, user_message: str, system_prompt: str, 
                         image_data: List[str] = None, trace_id: str = "", is_stream: bool = False) -> None:
        """
        记录聊天请求的详细信息
        
        Args:
            user_message: 用户消息
            system_prompt: 系统提示
            image_data: 图片数据列表
            trace_id: 追踪ID
            is_stream: 是否为流式请求
        """
        request_type = "流式聊天" if is_stream else "聊天"
        trace_info = f"[{trace_id}]" if trace_id else ""
        
        logger.info(f"{request_type}{trace_info} - System Prompt: {system_prompt}")
        logger.info(f"{request_type}{trace_info} - User Message: {user_message[:100]}...")
        
        if image_data:
            logger.info(f"{request_type}{trace_info} - 检测到多模态输入，包含 {len(image_data)} 张图片")
    
    async def _execute_tool_calls_if_needed(self, user_message: str, message_history: Any,
                                          system_prompt: str, rag_content: str,
                                          mcp_servers: List[McpServer]) -> Tuple[str, int]:
        """
        如果需要，执行工具调用
        
        Args:
            user_message: 用户消息
            message_history: 消息历史
            system_prompt: 系统提示
            rag_content: RAG上下文
            mcp_servers: MCP服务器列表
            
        Returns:
            更新后的RAG内容和工具调用消耗的token数量
        """
        if not mcp_servers:
            return rag_content, 0
            
        try:
            logger.info(f"执行工具调用，服务器数量: {len(mcp_servers)}")
            updated_rag, tool_prompt_tokens, _ = await self.execute_with_tools(
                user_message, message_history, system_prompt, rag_content, mcp_servers
            )
            logger.info(f"工具调用完成，消耗tokens: {tool_prompt_tokens}")
            return updated_rag, tool_prompt_tokens
        except Exception as e:
            logger.error(f"工具调用失败: {str(e)}")
            # 工具调用失败不应中断整个聊天流程
            return rag_content, 0
    
    def _create_tool_execution_chunk(self, prompt_tokens: int) -> Dict[str, Any]:
        """
        创建工具执行通知响应块
        
        Args:
            prompt_tokens: 提示token数量
            
        Returns:
            工具执行通知响应块
        """
        return {
            "content": "",
            "type": "tool_execution",
            "input_tokens": prompt_tokens,
            "output_tokens": 0,
            "done": False
        }
    
    def _create_error_response_chunk(self, error_message: str) -> Dict[str, Any]:
        """
        创建错误响应块
        
        Args:
            error_message: 错误消息
            
        Returns:
            错误响应块
        """
        return {
            "content": "非常抱歉,触发了智能体的拦截策略,不能回复您哦.....",
            "input_tokens": 0,
            "output_tokens": 0,
            "done": True,
            "error": error_message
        }
