from apps.paddleocr.runnable.paddleocr_runnable import PaddleOcrRunnable


def register_routes(app):
    PaddleOcrRunnable().register(app)