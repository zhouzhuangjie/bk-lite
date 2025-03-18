import os
from typing import List

from fastembed import TextEmbedding
from langchain_core.runnables import RunnableLambda
from langserve import add_routes


class FastEmbedRunnable:
    def __init__(self):
        model_name = 'BAAI/bge-small-zh-v1.5'
        if os.getenv("FAST_EMBED_MODEL_NAME"):
            model_name = os.getenv("FAST_EMBED_MODEL_NAME")

        self.embedding = TextEmbedding(model_name=model_name, cache_dir="models")

    def register(self, app):
        add_routes(app, RunnableLambda(self.execute).with_types(input_type=str, output_type=List[float]))

    def execute(self, text: str) -> List[float]:
        result = self.embedding.embed(text)
        result = [item for sublist in result for item in sublist.tolist()]
        return result
