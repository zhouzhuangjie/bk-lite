import os

from langchain_core.documents import Document

from src.rag.naive_rag.entity import ElasticSearchRetrieverRequest, ElasticSearchStoreRequest
from src.rag.naive_rag.rag import ElasticSearchRag
from dotenv import load_dotenv

load_dotenv()

def test_native_rag_ingest():
    rag = ElasticSearchRag()

    request = ElasticSearchStoreRequest(
        index_name=os.getenv('TEST_ELASTICSEARCH_RAG_INDEX'),
        index_mode='overwrite',
        docs=[
            Document(page_content='你好', metadata={'knowledge_title': '你好'}),
            Document(page_content='介绍一下你自己', metadata={'knowledge_title': '介绍一下你自己'}),
            Document(page_content='你是谁', metadata={'knowledge_title': '你是谁'}),
            Document(page_content='你会什么', metadata={'knowledge_title': '你会什么'}),
            Document(page_content='你能做什么', metadata={'knowledge_title': '你能做什么'}),
            Document(page_content='你能帮我做什么', metadata={'knowledge_title': '你能帮我做什么'}),
            Document(page_content='你能给我讲个笑话吗', metadata={'knowledge_title': '你能给我讲个笑话吗'}),
            Document(page_content='你能给我讲个故事吗', metadata={'knowledge_title': '你能给我讲个故事吗'}),
        ],
        embed_model_base_url=os.getenv('TEST_VLLM_BCE_EMBED_URL'),
        embed_model_api_key=os.getenv('TEST_VLLM_API_TOKEN'),
        embed_model_name=os.getenv("TEST_VLLM_BCE_EMBED_MODEL_NAME")
    )

    rag.ingest(request)

def test_native_rag():
    rag = ElasticSearchRag()

    request = ElasticSearchRetrieverRequest(
        index_name=os.getenv('TEST_ELASTICSEARCH_RAG_INDEX'),
        search_query="你好",
        size=10,
        embed_model_base_url=os.getenv('TEST_VLLM_BCE_EMBED_URL'),
        embed_model_api_key=os.getenv('TEST_VLLM_API_TOKEN'),
        embed_model_name=os.getenv("TEST_VLLM_BCE_EMBED_MODEL_NAME"),
        enable_rerank=True,
        rerank_model_base_url=os.getenv('TEST_VLLM_BCE_RERANK_URL'),
        rerank_top_k=2,
        rerank_model_api_key=os.getenv('TEST_VLLM_API_TOKEN'),
        rerank_model_name=os.getenv("TEST_VLLM_BCE_RERANK_MODEL_NAME"),
    )

    result = rag.search(request)
    print(result)
