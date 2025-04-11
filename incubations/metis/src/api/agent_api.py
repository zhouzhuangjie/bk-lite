from sanic import Blueprint, json

from src.core.web.api_auth import auth

agent_api_router = Blueprint("agent", url_prefix="/agent")


@agent_api_router.get("/invoke")
@auth.login_required
async def invoke(request):
    """
    调用智能体
    :param request:
    :return:
    """
    return json({"status": "success", "message": "Agent invoked successfully"})
