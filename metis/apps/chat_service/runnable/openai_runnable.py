from langchain_core.runnables import RunnableLambda

from langserve import add_routes
from loguru import logger

from apps.chat_service.driver.openai_driver import OpenAIDriver
from apps.chat_service.user_types.openai_chat_request import OpenAIChatRequest


class OpenAIRunnable():

    async def openai_chat(self, req: OpenAIChatRequest) -> str:
        driver = OpenAIDriver(
            openai_api_key=req.openai_api_key, openai_base_url=req.openai_api_base,
            temperature=req.temperature, model=req.model
        )
        llm_chat_history = driver.build_chat_history(req.chat_history, req.conversation_window_size)

        result = await driver.chat_with_history(
            system_prompt=req.system_message_prompt, user_message=req.user_message,
            message_history=llm_chat_history, rag_content=req.rag_context,
            mcp_servers=req.mcp_servers, trace_id=req.trace_id,
        )

        return result

    def register(self, app):
        add_routes(app,
                   RunnableLambda(self.openai_chat).with_types(input_type=OpenAIChatRequest, output_type=str),
                   path='/openai')
