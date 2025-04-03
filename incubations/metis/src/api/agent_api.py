from sanic import Blueprint

agent_api_router = Blueprint("agent", url_prefix="/agent")


@agent_api_router.get("/invoke")
async def invoke(request):
    """
    调用智能体
    :param request:
    :return:
    """
    pass
