from apps.olmocr.runnable.olmocr_runnable import OlmOcrRunnable


def register_routes(app):
    OlmOcrRunnable().register(app)
