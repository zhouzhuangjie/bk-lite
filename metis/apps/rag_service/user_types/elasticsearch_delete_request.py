from apps.rag_service.user_types.base_elasticsearch_request import BaseElasticSearchRequest


class ElasticSearchDeleteRequest(BaseElasticSearchRequest):
    index_name: str
    mode: str = "delete_index"
    metadata_filter: dict = {}
