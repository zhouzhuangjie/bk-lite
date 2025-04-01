import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()


def test_vllm_reranker():
    headers = {
        "accept": "application/json", "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('TEST_VLLM_API_TOKEN')}"
    }
    data = {
        "model": "maidalun/bce-reranker-base_v1",
        "query": "What is the capital of France?",
        "documents": [
            "The capital of Brazil is Brasilia.",
            "The capital of France is Paris.", "Horses and cows are both animals"
        ]
    }
    response = requests.post(os.getenv('TEST_VLLM_BCE_RERANK_URL'), headers=headers, json=data)
    print(json.dumps(response.json(), indent=2))
