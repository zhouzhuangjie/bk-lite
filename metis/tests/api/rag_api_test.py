import os

import requests
from dotenv import load_dotenv

load_dotenv()


def test_ingest():
    rs = requests.post('http://localhost:18083/api/rag/ingest',
                       files={'file': open(
                           'tests/assert/full_text_loader.txt', 'rb')},
                       data={
                           "index_name": os.getenv('TEST_ELASTICSEARCH_RAG_INDEX'),
                           "embed_model_base_url": os.getenv('TEST_VLLM_BCE_EMBED_URL'),
                           "embed_model_api_key": os.getenv('TEST_VLLM_API_TOKEN'),
                           "embed_model_name": os.getenv("TEST_VLLM_BCE_EMBED_MODEL_NAME"),
                           "chunk_mode": "fixed_size",
                           "chunk_size": 512,
                           "knowledge_id": "1"
                       })
    print(rs.json())
