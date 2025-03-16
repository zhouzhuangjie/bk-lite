from langchain_core.runnables import RunnableLambda
from langchain_community.chat_message_histories import ChatMessageHistory
from langserve import add_routes
from loguru import logger

from apps.chat_service.driver.openai_driver import OpenAIDriver
from apps.chat_service.user_types.openai_chat_request import OpenAIChatRequest


class OpenAIRunnable():
    async def openai_chat(self, req: OpenAIChatRequest) -> str:
        driver = OpenAIDriver(
            openai_api_key=req.openai_api_key,
            openai_base_url=req.openai_api_base,
            temperature=req.temperature,
            model=req.model,
        )

        llm_chat_history = ChatMessageHistory()

        if req.chat_history:
            for event in req.chat_history[-req.conversation_window_size:]:
                if event.text is None:
                    logger.debug("Skipping event with None text:{event}")
                    continue

                if event.event == "user":
                    llm_chat_history.add_user_message(event.text)
                elif event.event == "bot":
                    llm_chat_history.add_ai_message(event.text)

        result = await driver.chat_with_history(
            system_prompt=req.system_message_prompt,
            user_message=req.user_message,
            message_history=llm_chat_history,
            rag_content=req.rag_context,
            mcp_servers=req.mcp_servers,
            trace_id=req.trace_id,
        )

        return result

    def register(self, app):
        add_routes(app,
                   RunnableLambda(self.openai_chat).with_types(input_type=OpenAIChatRequest, output_type=str),
                   path='/openai')
