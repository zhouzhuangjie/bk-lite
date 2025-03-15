from typing import List

from langchain_core.documents import Document
from langchain_core.runnables import RunnableLambda
from langserve import add_routes

from core.runnable.ocr_runnable import OcrRunnable
from core.user_types.ocr_request import OcrRequest


class OlmOcrRunnable(OcrRunnable):
    def __init__(self):
        pass

    def predict(self, file_path: str) -> List[Document]:
        return super().predict(file_path)

    def register(self, app):
        add_routes(app,
                   RunnableLambda(self.execute).with_types(input_type=OcrRequest, output_type=List[Document]),
                   path='/olmocr/execute')
