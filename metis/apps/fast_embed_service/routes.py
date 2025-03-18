from apps.fast_embed_service.runnable.fast_embed_runnable import FastEmbedRunnable


def register_routes(app):
    FastEmbedRunnable().register(app)
