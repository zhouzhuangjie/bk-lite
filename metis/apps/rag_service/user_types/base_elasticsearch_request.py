from langserve import CustomUserType


class BaseElasticSearchRequest(CustomUserType):
    elasticsearch_url: str = "http://elasticsearch.ops-pilot:9200"
    elasticsearch_password: str
