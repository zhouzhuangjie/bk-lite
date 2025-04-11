from sanic import Blueprint, json

from src.core.web.api_auth import auth
from src.service.chatbot_workflow.entity.chatbot_workflow_request import ChatBotWorkflowRequest
from sanic_ext import validate
from src.service.chatbot_workflow.entity.chatbot_workflow_response import ChatBotWorkflowResponse
from src.service.chatbot_workflow.graph.chatbot_workflow_graph import ChatBotWorkflowGraph
from src.service.react_agent.entity.react_agent_request import ReActAgentRequest
from src.service.react_agent.graph.react_agent_graph import ReActAgentGraph
agent_api_router = Blueprint("agent", url_prefix="/agent")


@agent_api_router.post("/invoke_chatbot_workflow")
@auth.login_required
@validate(json=ChatBotWorkflowRequest)
def invoke_chatbot_workflow(request, body: ChatBotWorkflowRequest):
    workflow = ChatBotWorkflowGraph()
    body.naive_rag_request.search_query = body.user_message
    result = workflow.execute(body)
    return json(result.model_dump())


@agent_api_router.post("/invoke_react_agent")
@auth.login_required
@validate(json=ReActAgentRequest)
async def invoke_react_agent(request, body: ReActAgentRequest):
    graph = ReActAgentGraph()
    body.naive_rag_request.search_query = body.user_message
    result = await graph.execute(body)
    return json(result.model_dump())
