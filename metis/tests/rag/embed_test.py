import os

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from loguru import logger


def test_vllm_embed():
    client = OpenAIEmbeddings(
        model=os.getenv('TEST_BCE_EMBED_MODEL'),
        api_key=os.getenv('TEST_INFERENCE_TOKEN'),
        base_url=os.getenv('TEST_INFERENCE_BASE_URL'),
    )
    responses = client.embed_documents([
        "介绍"
    ])

    logger.info(responses)
