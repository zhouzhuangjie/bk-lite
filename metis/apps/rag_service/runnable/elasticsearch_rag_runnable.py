from typing import List

from langchain_core.documents import Document
from langchain_core.runnables import RunnableLambda
from langchain_elasticsearch import ElasticsearchRetriever
from langserve import RemoteRunnable, add_routes

from apps.rag_service.query.query_builder import ElasticsearchQueryBuilder
from apps.rag_service.user_types.elasticsearch_retriever_request import ElasticSearchRetrieverRequest


class ElasticSearchRagRunnable:

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
            url=req.elasticsearch_url,
            username="elastic",
            password=req.elasticsearch_password,
        )

        # 执行搜索
        search_result = documents_retriever.invoke(req.search_query)
        search_result = self._process_search_result(search_result)

        # 重排序处理
        if req.enable_rerank:
            reranker = RemoteRunnable(req.rerank_model_address)
            search_result = reranker.invoke({
                "docs": search_result,
                "query": req.search_query,
                "top_n": req.rerank_top_k
            })

        return search_result

    def register(self, app):
        add_routes(app,
                   RunnableLambda(self.execute).with_types(input_type=ElasticSearchRetrieverRequest,
                                                           output_type=List[Document]),
                   path='/elasticsearch_rag')
