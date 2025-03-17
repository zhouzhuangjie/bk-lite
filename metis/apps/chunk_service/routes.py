from apps.chunk_service.runnable.file_chunk_runnable import FileChunkRunnable
from apps.chunk_service.runnable.manual_chunk_runnable import ManualChunkRunnable
from apps.chunk_service.runnable.web_page_chunk_runnable import WebPageChunkRunnable


def register_routes(app):
    FileChunkRunnable().register(app)
    WebPageChunkRunnable().register(app)
    ManualChunkRunnable().register(app)
