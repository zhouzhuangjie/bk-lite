import elasticsearch
from langchain_core.runnables import RunnableLambda
from langserve import add_routes
from loguru import logger

from apps.rag_service.user_types.elasticsearch_delete_request import ElasticSearchDeleteRequest
from core.server_settings import server_settings


class ElasticSearchDeleteRunnable:
    def __init__(self):
        pass

    def execute(self, req: ElasticSearchDeleteRequest) -> bool:
        try:
            es = elasticsearch.Elasticsearch(hosts=[server_settings.elasticsearch_url],
                                             basic_auth=("elastic", server_settings.elasticsearch_password))
            if req.mode == "delete_index":
                es.indices.delete(index=req.index_name)
            if req.mode == "delete_docs":
                metadata_filter = []
                for key, value in req.metadata_filter.items():
                    metadata_filter.append({"term": {f"metadata.{key}.keyword": value}})

                query = {
                    "query": {
                        "bool": {
                            "filter": metadata_filter
                        }
                    }
                }

                es.delete_by_query(index=req.index_name, body=query)
            return True
        except Exception as e:
            logger.error(f"delete index failed: {req.index_name}, {e}")
            return False

    def register(self, app):
        add_routes(app,
                   RunnableLambda(self.execute).with_types(input_type=ElasticSearchDeleteRequest, output_type=bool),
                   path='/elasticsearch_delete')
