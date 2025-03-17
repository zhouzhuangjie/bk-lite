from apps.rag_service.user_types.base_elasticsearch_request import BaseElasticSearchRequest


class ElasticSearchRequest(BaseElasticSearchRequest):
    embed_model_address: str = "http://fast-embed-server.ops-pilot"
