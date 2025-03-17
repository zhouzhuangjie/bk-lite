from apps.rag_service.runnable.elasticsearch_delete_runnable import ElasticSearchDeleteRunnable
from apps.rag_service.runnable.elasticsearch_index_runnable import ElasticSearchIndexRunnable
from apps.rag_service.runnable.elasticsearch_rag_runnable import ElasticSearchRagRunnable


def register_routes(app):
    ElasticSearchDeleteRunnable().register(app)
    ElasticSearchIndexRunnable().register(app)
    ElasticSearchRagRunnable().register(app)
