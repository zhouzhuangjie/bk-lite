from langchain_core.documents import Document

from src.ocr.base_ocr import BaseOCR


class ImageLoader:
    def __init__(self, path, ocr: BaseOCR):
        self.path = path
        self.ocr = ocr

    def load(self):
        docs = []
        result = self.ocr.predict(self.path)
        doc = Document(page_content=result, metadata={"format": "image"})
        docs.append(doc)
        return docs
