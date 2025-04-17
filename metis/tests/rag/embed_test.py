import os

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

load_dotenv()


def test_vllm_embed():
    client = OpenAIEmbeddings(
        model='bce-embedding-base_v1',
        api_key=os.getenv('TEST_INFERENCE_TOKEN'),
        base_url=os.getenv('TEST_INFERENCE_BASE_URL'),
    )
    responses = client.embed_documents([
        "介绍"
    ])

    print(responses)
