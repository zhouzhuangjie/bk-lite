from typing import List

from langchain_core.documents import Document
from langchain_core.runnables import RunnableLambda
from langserve import add_routes

from apps.bce_embed_service.user_types.rerank_request import ReRankerRequest
from apps.bce_embed_service.utils.bce_rerank import BCERerank


class BCEReRankRunnable:
    def __init__(self):
        self.reranker = BCERerank()

    def register(self, app):
        add_routes(app,
                   RunnableLambda(self.execute).with_types(input_type=ReRankerRequest, output_type=List[Document]),
                   path='/rerank')

    def execute(self, req: ReRankerRequest) -> List[float]:
        self.reranker.top_n = req.top_n
        compressed_data = self.reranker.compress_documents(req.docs, req.query)
        return compressed_data
