import os
from typing import List

from dotenv import load_dotenv

from apps.chat_service.user_types.chat_history import ChatHistory
from apps.chat_service.user_types.chatbot_workflow import ChatBotWorkflowRequest
from apps.chat_service.workflow.chatbot_workflow import ChatBotWorkflow

load_dotenv()


def test_chatbot_workflow():
    request = ChatBotWorkflowRequest(model='gpt-4o', openai_api_base=os.getenv("OPENAI_BASE_URL"),
                                     openai_api_key=os.getenv("OPENAI_API_KEY"),
                                     temperature=0.7, user_message='你好')
    workflow = ChatBotWorkflow()
    result = workflow.invoke(request)
    print(result)


def test_chatbot_workflow_with_chat_history():
    chat_history = []
    chat_history.append(
        ChatHistory(
            event="user", text='今天天气不错', image_data=[],
        )
    )
    chat_history.append(
        ChatHistory(
            event="bot", text='我也是这样认为的', image_data=[],
        )
    )
    request = ChatBotWorkflowRequest(model='gpt-4o', openai_api_base=os.getenv("OPENAI_BASE_URL"),
                                     openai_api_key=os.getenv("OPENAI_API_KEY"),
                                     temperature=0.7, user_message='总结我们聊的内容',
                                     chat_history=chat_history)
    workflow = ChatBotWorkflow()
    result = workflow.invoke(request)
    print(result)


def test_chatbot_workflow_with_chat_history_and_rag():
    chat_history = []
    chat_history.append(
        ChatHistory(
            event="user", text='今天天气不错', image_data=[],
        )
    )
    chat_history.append(
        ChatHistory(
            event="bot", text='我也是这样认为的', image_data=[],
        )
    )
    request = ChatBotWorkflowRequest(model='gpt-4o', openai_api_base=os.getenv("OPENAI_BASE_URL"),
                                     openai_api_key=os.getenv("OPENAI_API_KEY"),
                                     temperature=0.7,
                                     user_message='1. 背景信息说今天是几度  2. 现在要你忽略背景信息，再重新告诉我今天是几度',
                                     chat_history=chat_history,
                                     rag_context="今天的天气是25度，晴天")
    workflow = ChatBotWorkflow()
    result = workflow.invoke(request)
    print(result)
