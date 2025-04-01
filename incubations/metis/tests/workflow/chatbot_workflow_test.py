import os

from dotenv import load_dotenv
from langgraph.checkpoint.postgres import PostgresSaver

from src.workflow.chatbot_workflow.entity import ChatBotWorkflowResponse, ChatBotWorkflowRequest
from src.workflow.chatbot_workflow.graph import ChatBotWorkflowGraph

load_dotenv()


def test_chat():
    request = ChatBotWorkflowRequest(
        model="gpt-4o",
        openai_api_base=os.getenv("OPENAI_BASE_URL"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        user_message="你是谁",
        system_message_prompt="你是一个智能运维机器人，名字叫Metis",
        user_id="1",
        thread_id="2"
    )

    with PostgresSaver.from_conn_string(os.getenv('DB_URI')) as checkpoint:
        workflow = ChatBotWorkflowGraph(request, checkpoint)
        graph = workflow.build_graph()

        config = {"configurable": {"thread_id": request.thread_id, "user_id": request.user_id}}
        result = graph.invoke(request, config)
        response = ChatBotWorkflowResponse(message=result["messages"][-1].content,
                                           total_tokens=result["messages"][-1].response_metadata['token_usage'][
                                               'total_tokens'])
        print(response)
