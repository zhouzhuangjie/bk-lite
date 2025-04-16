from typing import List
from langchain_community.document_loaders import RecursiveUrlLoader
from langchain_community.document_transformers import BeautifulSoupTransformer
from langchain_core.documents import Document


class WebSiteLoader:
    def __init__(self, url, max_depth):
        self.url = url
        self.max_depth = max_depth

    def load(self) -> List[Document]:
        loader = RecursiveUrlLoader(self.url, max_depth=self.max_depth)
        web_docs = loader.load()
        transformer = BeautifulSoupTransformer()
        docs = transformer.transform_documents(web_docs)
        return docs
