# -- coding: utf-8 --
# @File: collect.py
# @Time: 2025/2/27 10:41
# @Author: windyzhao

from sanic import Blueprint, json
from sanic.log import logger
from sanic import response

from service.collect_service import CollectService

collect_router = Blueprint("collect", url_prefix="/collect")


@collect_router.get("/collect_info")
async def collect(request):
    params = {i[0]: i[1] for i in request.query_args}
    collect_service = CollectService(params)
    metrics_data = collect_service.collect()
    logger.info("Metrics data generated....")
    return response.raw(metrics_data, content_type='text/plain; version=0.0.4; charset=utf-8')


@collect_router.post("/collect/list_regions/")
async def list_regions(request):
    # 获取 POST 请求中的 JSON 数据
    data = request.json

    # 返回一个 JSON 响应
    return json({"result": True, "data": data})


@collect_router.post("/collect/test_connection/")
async def test_connection(request):
    # 获取 POST 请求中的 JSON 数据
    data = request.json

    # 返回一个 JSON 响应
    return json({"result": True, "data": data})
