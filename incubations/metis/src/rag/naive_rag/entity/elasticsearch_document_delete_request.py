from pydantic import BaseModel


class ElasticSearchDeleteRequest(BaseModel):
    index_name: str
    mode: str = "delete_index"
    metadata_filter: dict = {}
