import os
from typing import List

import requests
from langchain_core.documents import Document
from langchain_elasticsearch import ElasticsearchRetriever

from src.core.rag.naive_rag.entity import ElasticSearchRetrieverRequest
from src.core.rag.naive_rag.query_builder import ElasticsearchQueryBuilder


class ElasticSearchRag:
    def _process_search_result(self, docs: List[Document]) -> List[Document]:
        for doc in docs:
            if 'vector' in doc.metadata.get('_source', {}):
                del doc.metadata['_source']['vector']
        return docs

    def execute(self, req: ElasticSearchRetrieverRequest) -> List[Document]:
        # 构建检索器 (使用固定的size)
        documents_retriever = ElasticsearchRetriever.from_es_params(
            index_name=req.index_name,
            body_func=lambda x: ElasticsearchQueryBuilder.build_query(req),
            content_field="text",
            url=os.getenv('ELASTICSEARCH_URL'),
            username="elastic",
            password=os.getenv('ELASTICSEARCH_PASSWORD'),
        )

        # 执行搜索
        search_result = documents_retriever.invoke(req.search_query)
        search_result = self._process_search_result(search_result)

        # 重排序处理
        if req.enable_rerank:
            headers = {
                "accept": "application/json", "Content-Type": "application/json",
                "Authorization": f"Bearer {req.rerank_model_api_key}"
            }
            data = {
                "model": req.rerank_model_name,
                "query": req.search_query,
                "documents": req.documents,
            }
            response = requests.post(req.rerank_model_base_url, headers=headers, json=data)
            #TODO
            rerank_result = response.json()
            search_result = None

        return search_result
