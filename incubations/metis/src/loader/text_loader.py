from typing import List

from sanic.log import logger

from langchain_core.documents import Document
from langchain_core.document_loaders import BaseLoader


class TextLoader(BaseLoader):
    def __init__(self, path):
        self.path = path

    def load(self) -> List[Document]:
        docs: List[Document] = []
        logger.info(f'loading text file: {self.path} with full text mode')
        with open(self.path, 'r', encoding="utf-8") as f:
            full_text = f.read()
            docs.append(Document(full_text))
        return docs
