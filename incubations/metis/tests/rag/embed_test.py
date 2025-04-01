import os

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

load_dotenv()


def test_vllm_embed():
    client = OpenAIEmbeddings(
        model=os.getenv("TEST_VLLM_BCE_EMBED_MODEL_NAME"),
        api_key=os.getenv('TEST_VLLM_API_TOKEN'),
        base_url=os.getenv('TEST_VLLM_BCE_EMBED_URL'),
    )
    responses = client.embed_documents([
        "介绍"
    ])

    print(responses)
