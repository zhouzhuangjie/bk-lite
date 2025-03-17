from typing import List

from langchain_core.documents import Document

from apps.rag_service.user_types.base_elasticsearch_request import BaseElasticSearchRequest


class ElasticSearchStoreRequest(BaseElasticSearchRequest):
    embed_model_address: str = "http://fast-embed-server.ops-pilot"
    index_name: str
    index_mode: str
    chunk_size: int = 50
    max_chunk_bytes: int = 200000000
    docs: List[Document]
