from apps.cloudocr.runnable.azure_ocr_runnable import AzureOcrRunnable


def register_routes(app):
    AzureOcrRunnable().register(app)
