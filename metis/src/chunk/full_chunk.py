from typing import List

from langchain_core.documents import Document


class FullChunk:
    def chunk(self, docs: List[Document]) -> List[Document]:
        for doc in docs:
            doc.metadata['chunk_number'] = str(0)
        return docs
