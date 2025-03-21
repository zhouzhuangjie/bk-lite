import json
import time
import base64
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


class OpenAIDriver():
    def __init__(self, openai_api_key, openai_base_url, temperature, model):
        super().__init__()

        self.client = ChatOpenAI(
            openai_api_key=openai_api_key, openai_api_base=openai_base_url,
            temperature=temperature, model=model, max_retries=3,
        )

        self.streaming_client = ChatOpenAI(
            openai_api_key=openai_api_key,
            openai_api_base=openai_base_url,
            temperature=temperature,
            model=model,
            streaming=True,
            max_retries=3,
        )

        try:
            self.encoding = tiktoken.encoding_for_model(model)
        except Exception:
            self.encoding = tiktoken.get_encoding("cl100k_base")

    def build_chat_history(self, chat_history: List[ChatHistory], window_size: int) -> ChatMessageHistory:
        llm_chat_history = ChatMessageHistory()

        if chat_history:
            for event in chat_history[-window_size:]:
                if event.text is None:
                    logger.debug("Skipping event with None text:{event}")
                    continue

                if event.event == "user":
                    llm_chat_history.add_user_message(event.text)
                elif event.event == "bot":
                    llm_chat_history.add_ai_message(event.text)

        return llm_chat_history

    def count_tokens(self, text: str) -> int:
        """计算文本的 token 数量"""
        if not text:
            return 0
        return len(self.encoding.encode(text))

    def count_message_tokens(self, messages: List[Dict]) -> Tuple[int, int]:
        """计算消息列表的输入和输出 token 数量"""
        input_tokens = output_tokens = 0

        for message in messages:
            content = message.content
            input_tokens += self.count_tokens(content)

        return input_tokens, output_tokens

    def create_simple_chain(self, system_content):
        """创建简单的对话链"""
        simple_prompt = ChatPromptTemplate.from_messages([
            ("system", system_content),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
        ])
        return simple_prompt | self.client

    def _format_multimodal_message(self, user_message: str, image_data: Optional[List[str]] = None) -> Union[
        str, List[Dict]]:
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
                    "url": f"data:image/jpeg;base64,{img}"
                }
            })

        return content

    def _create_multimodal_message(self, content: Union[str, List[Dict]]) -> HumanMessage:
        """
        创建多模态消息对象

        Args:
            content: 消息内容，可以是字符串或包含文本和图片的列表

        Returns:
            HumanMessage对象
        """
        return HumanMessage(content=content)

    def _invoke_simple_chain(self, user_message: str,
                             message_history: Any,
                             system_prompt: str,
                             rag_content: str,
                             trace_id: str,
                             image_data: List[str] = []):
        start_time = time.time()
        logger.info(f"问题[{trace_id}]: {user_message}")

        # 计算输入 token
        system_content = f"{system_prompt}, Here is some context: {rag_content.replace('{', '').replace('}', '')}"
        input_tokens = self.count_tokens(system_content) + self.count_tokens(user_message)

        # 为历史消息计算 token
        if hasattr(message_history, "messages") and message_history.messages:
            hist_input, hist_output = self.count_message_tokens(message_history.messages)
            input_tokens += hist_input + hist_output

        # 处理多模态输入
        if image_data:
            logger.info(f"处理多模态输入，包含 {len(image_data)} 张图片")
            formatted_content = self._format_multimodal_message(user_message, image_data)
            human_message = self._create_multimodal_message(formatted_content)

            # 使用直接调用方式处理多模态输入
            messages = [
                {"role": "system", "content": system_content}
            ]

            # 添加历史消息
            if hasattr(message_history, "messages") and message_history.messages:
                messages.extend(message_history.messages)

            # 添加当前带图片的消息
            messages.append({"role": "user", "content": human_message.content})

            # 直接调用LLM
            result = self.client.invoke(messages)

        else:
            # 使用普通链处理纯文本
            chain = self.create_simple_chain(system_content)
            chain_with_history = RunnableWithMessageHistory(
                chain,
                get_session_history=lambda: message_history,
                input_messages_key="input",
                history_messages_key="chat_history",
            )
            result = chain_with_history.invoke({"input": user_message})

        # 计算输出 token
        output_tokens = self.count_tokens(result.content)

        end_time = time.time()
        duration = end_time - start_time

        # 添加 token 计数到结果
        result.usage_metadata = {
            'input_tokens': input_tokens,
            'output_tokens': output_tokens
        }

        logger.info(f"Result type: {result.response_metadata}")
        logger.info(f"耗时:[{duration:.4f}秒],回复[{trace_id}]: {result}")
        return result

    async def execute_with_tools(self, user_message, message_history, system_prompt, rag_content, mcp_servers):
        """使用工具执行查询"""
        mcp_config = {
            server.name: {
                "url": server.url,
                "transport": 'sse'
            } for server in mcp_servers
        }

        total_prompt_tokens = total_completion_tokens = 0

        async with MultiServerMCPClient(mcp_config) as mcp_server:
            tools = mcp_server.get_tools()

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

            input_data = {
                "input": user_message,
                "chat_history": message_history.messages,
                "rag_content": rag_content,
                "tools": [tool.name for tool in tools],
                "system_prompt": system_prompt,
            }

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
            rag_content += f"""
                            <function_call_thought>
                                {thoughts_result}
                            </function_call_thought>
                            """
            total_completion_tokens = self.count_tokens(thoughts_result)

        return rag_content, total_prompt_tokens, total_completion_tokens

    async def chat_with_history(self, system_prompt: str, user_message: str,
                                message_history: List[ChatHistory], rag_content: str = "",
                                mcp_servers: List[McpServer] = [], trace_id: str = '',
                                image_data: List[str] = []) -> str:
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

            # 获取最终结果
            simple_result = self._invoke_simple_chain(
                user_message, message_history, system_prompt, rag_content, trace_id, image_data
            )

            # 更新token计数
            total_prompt_tokens += simple_result.usage_metadata['input_tokens']
            total_completion_tokens += simple_result.usage_metadata['output_tokens']

            return json.dumps({
                "result": True,
                "data": {
                    "content": simple_result.content,
                    "input_tokens": total_prompt_tokens,
                    "output_tokens": total_completion_tokens,
                }
            }, ensure_ascii=False, indent=4)

        except Exception as e:
            logger.exception(f"Error during chat execution: {str(e)}")
            return json.dumps({
                "result": True,
                "data": {
                    "content": "非常抱歉,触发了智能体的拦截策略,不能回复您哦.....",
                    "input_tokens": 0,
                    "output_tokens": 0,
                }
            }, ensure_ascii=False, indent=4)

    async def _stream_invoke_simple_chain(self, user_message: str,
                                          message_history: Any,
                                          system_prompt: str,
                                          rag_content: str,
                                          trace_id: str,
                                          image_data: List[str] = []) -> AsyncIterator[Dict[str, Any]]:
        """流式方式调用简单对话链"""
        start_time = time.time()
        logger.info(f"流式问题[{trace_id}]: {user_message}")

        # 计算输入 token
        system_content = f"{system_prompt}, Here is some context: {rag_content.replace('{', '').replace('}', '')}"
        input_tokens = self.count_tokens(system_content) + self.count_tokens(user_message)

        # 为历史消息计算 token
        if hasattr(message_history, "messages") and message_history.messages:
            hist_input, hist_output = self.count_message_tokens(message_history.messages)
            input_tokens += hist_input + hist_output

        # 确保LLM启用流式模式
        streaming_client = self.streaming_client

        # 处理多模态输入
        if image_data:
            logger.info(f"流式处理多模态输入，包含 {len(image_data)} 张图片")
            formatted_content = self._format_multimodal_message(user_message, image_data)
            human_message = self._create_multimodal_message(formatted_content)

            # 使用直接调用方式处理多模态输入
            messages = [
                {"role": "system", "content": system_content}
            ]

            # 添加历史消息
            if hasattr(message_history, "messages") and message_history.messages:
                messages.extend(message_history.messages)

            # 添加当前带图片的消息
            messages.append({"role": "user", "content": human_message.content})

            # 流式响应
            output_tokens = 0
            final_text = ""

            # 直接调用LLM的流式接口
            async for chunk in streaming_client.astream(messages):
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
            # 使用普通链处理纯文本
            simple_prompt = ChatPromptTemplate.from_messages([
                ("system", system_content),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
            ])
            chain = simple_prompt | streaming_client

            chain_with_history = RunnableWithMessageHistory(
                chain,
                get_session_history=lambda: message_history,
                input_messages_key="input",
                history_messages_key="chat_history",
            )

            output_tokens = 0
            final_text = ""

            async for chunk in chain_with_history.astream({"input": user_message}):
                if chunk.content:
                    final_text += chunk.content
                    output_tokens = self.count_tokens(final_text)
                    yield {
                        "content": chunk.content,
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "done": False
                    }

        end_time = time.time()
        duration = end_time - start_time

        # 发送完成消息
        logger.info(f"流式耗时:[{duration:.4f}秒],完成回复[{trace_id}]")
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
        """流式方式与历史对话"""
        try:
            logger.info(f"流式聊天 - System Prompt: {system_prompt}, User Message: {user_message}")
            if image_data:
                logger.info(f"流式检测到多模态输入，包含 {len(image_data)} 张图片")

            total_prompt_tokens = 0

            # 如果有工具服务器，先执行工具调用
            if mcp_servers:
                rag_content, tool_prompt_tokens, _ = await self.execute_with_tools(
                    user_message, message_history, system_prompt, rag_content, mcp_servers
                )
                total_prompt_tokens += tool_prompt_tokens

                # 发送工具调用的通知
                yield {
                    "content": "",
                    "type": "tool_execution",
                    "input_tokens": total_prompt_tokens,
                    "output_tokens": 0,
                    "done": False
                }

            # 流式获取最终结果
            async for chunk in self._stream_invoke_simple_chain(
                    user_message, message_history, system_prompt, rag_content, trace_id, image_data
            ):
                # 更新token计数
                chunk["input_tokens"] += total_prompt_tokens
                yield chunk

        except Exception as e:
            logger.exception(f"流式聊天错误: {str(e)}")
            yield {
                "content": "非常抱歉,触发了智能体的拦截策略,不能回复您哦.....",
                "input_tokens": 0,
                "output_tokens": 0,
                "done": True,
                "error": str(e)
            }
