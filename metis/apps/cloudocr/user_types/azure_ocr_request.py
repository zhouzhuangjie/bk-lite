from core.user_types.ocr_request import OcrRequest


class AzureOcrRequest(OcrRequest):
    azure_ocr_endpoint: str
    azure_ocr_key: str
