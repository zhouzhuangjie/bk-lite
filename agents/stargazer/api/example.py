from sanic import Blueprint
from sanic.log import logger

example_router = Blueprint("example", url_prefix="/example")


@example_router.get("/metrics")
async def metrics(request):
    from prometheus_client import Counter, generate_latest
    from sanic import Sanic, response
    REQUEST_COUNT = Counter('request_count', 'Total request count')
    REQUEST_COUNT.inc()
    metrics_data = generate_latest()

    logger.info("Metrics data generated....")

    return response.raw(metrics_data, content_type='text/plain; version=0.0.4; charset=utf-8')
