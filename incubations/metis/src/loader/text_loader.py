import os
from typing import List

from sanic.log import logger

from langchain_core.documents import Document
from sqlalchemy.testing.suite.test_reflection import metadata


class TextLoader():
    def __init__(self, path):
        self.path = path

    def load(self) -> List[Document]:
        docs = []
        logger.info(f'loading text file: {self.path} with full text mode')
        with open(self.path, 'r', encoding="utf-8") as f:
            full_text = f.read()
            docs.append(Document(full_text))
        return docs
