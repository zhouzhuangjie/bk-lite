from typing import List
from langchain_core.documents import Document


class MarkdownLoader:
    def __init__(self, path: str):
        self.path = path

    def load(self) -> List[Document]:
        docs: List[Document] = []
        with open(self.path, 'r', encoding='utf-8') as file:
            content = file.read()
            docs.append(Document(content))
        return docs
