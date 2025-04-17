import os

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from src.chunk.recursive_chunk import RecursiveChunk
from src.chunk.semantic_chunk import SemanticChunk
from src.loader.text_loader import TextLoader

load_dotenv()


def test_recursive_chunk():

    chunk = RecursiveChunk()
    loader = TextLoader(path='../assert/full_text_loader.txt')
    docs = loader.load()
    rs = chunk.chunk(docs)
    print(rs)
