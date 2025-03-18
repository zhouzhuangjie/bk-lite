from langserve import add_routes

from apps.bce_embed_service.runnable.bce_embed_runnable import BCEEmbedRunnable
from apps.bce_embed_service.runnable.bce_rerank_runnable import BCEReRankRunnable


def register_routes(app):
    BCEReRankRunnable().register(app)
    BCEEmbedRunnable().register(app)
