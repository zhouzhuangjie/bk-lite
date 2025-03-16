import json
import time
from typing import List, Any, Dict, Tuple

from langchain.agents import initialize_agent, AgentType
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
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

    def _invoke_simple_chain(self, user_message: str,
                             message_history: Any,
                             system_prompt: str,
                             rag_content: str,
                             trace_id: str):
        start_time = time.time()
        logger.info(f"问题[{trace_id}]: {user_message}")

        # 计算输入 token
        system_content = f"{system_prompt}, Here is some context: {rag_content.replace('{', '').replace('}', '')}"
        input_tokens = self.count_tokens(system_content) + self.count_tokens(user_message)

        # 为历史消息计算 token
        if hasattr(message_history, "messages") and message_history.messages:
            hist_input, hist_output = self.count_message_tokens(message_history.messages)
            input_tokens += hist_input + hist_output

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
                                mcp_servers: List[McpServer] = [], trace_id: str = '') -> str:
        try:
            logger.info(f"System Prompt: {system_prompt}, User Message: {user_message},mcp_servers:{mcp_servers}")

            total_prompt_tokens = total_completion_tokens = 0

            # 如果有工具服务器，先执行工具调用
            if mcp_servers:
                rag_content, tool_prompt_tokens, tool_completion_tokens = await self.execute_with_tools(
                    user_message, message_history, system_prompt, rag_content, mcp_servers
                )

            # 获取最终结果
            simple_result = self._invoke_simple_chain(
                user_message, message_history, system_prompt, rag_content, trace_id
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
