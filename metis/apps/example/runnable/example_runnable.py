from langchain_core.runnables import RunnableLambda
from langserve import add_routes
from loguru import logger
from apps.example.user_types.example import ExampleUserType


class ExampleRunnable:
    def __init__(self):
        pass

    def register(self, app):
        add_routes(app,
                   RunnableLambda(self.example).with_types(input_type=ExampleUserType, output_type=str),
                   path='/example')

    def example(self, req: ExampleUserType) -> str:
        logger.info(f"msg: {req.msg}")
        return req.msg
