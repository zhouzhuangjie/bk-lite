from typing import List
from pydantic.v1 import BaseModel  # 添加 pydantic v1 导入

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_core.runnables import RunnableLambda
from langserve import add_routes

from apps.bce_embed_service.user_types.rerank_request import ReRankerRequest


class BCEEmbedRunnable:
    def __init__(self):
        self.embedding = HuggingFaceEmbeddings(
            model_name="./models/bce-embedding-base_v1",
            encode_kwargs={
                "normalize_embeddings": True,
                "batch_size": 32,
            },
        )

    def register(self, app):
        add_routes(app,
                   RunnableLambda(self.execute).with_types(input_type=str, output_type=List[float]),
                   path='/embed')

    def execute(self, req: str) -> List[float]:
        return self.embedding.embed_query(req)
