import os

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from src.chunk.semantic_chunk import SemanticChunk
from src.loader.text_loader import TextLoader

load_dotenv()


def test_semantic_chunk():
    embeddings = OpenAIEmbeddings(
        model=os.getenv("TEST_VLLM_BCE_EMBED_MODEL_NAME"),
        api_key=os.getenv('TEST_VLLM_API_TOKEN'),
        base_url=os.getenv('TEST_VLLM_BCE_EMBED_URL'),
    )

    chunk = SemanticChunk(embeddings)
    loader = TextLoader(path='../assert/full_text_loader.txt')
    docs = loader.load()
    rs = chunk.chunk(docs)
    print(rs)
