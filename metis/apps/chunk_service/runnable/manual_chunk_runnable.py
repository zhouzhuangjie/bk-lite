from typing import List

from langchain_core.documents import Document
from langchain_core.runnables import RunnableLambda
from langserve import add_routes

from apps.chunk_service.runnable.base_chunk_runnable import BaseChunkRunnable
from apps.chunk_service.user_types.manual_chunk_request import ManualChunkRequest


class ManualChunkRunnable(BaseChunkRunnable):
    def __init__(self):
        pass

    def parse(self, request: ManualChunkRequest) -> List[Document]:
        docs = [Document(request.content)]
        return self.parse_docs(docs, request)

    def register(self, app):
        add_routes(app,
                   RunnableLambda(self.parse).with_types(input_type=ManualChunkRequest, output_type=List[Document]),
                   path='/manual_chunk')
