import os

from langchain_openai import ChatOpenAI
from loguru import logger

from src.chunk.fixed_size_chunk import FixedSizeChunk
from src.enhance.qa_enhance import QAEnhance
from src.entity.rag.qa_enhance_request import QAEnhanceRequest
from src.loader.markdown_loader import MarkdownLoader


def test_qa_enhance():
    loader = MarkdownLoader(path='../readme.md')
    doc = loader.load()
    chunk = FixedSizeChunk()
    rs = chunk.chunk(doc)

    for t in rs:
        req = QAEnhanceRequest(
            size=10,
            content=t.page_content,
            model="gpt-4o",
            openai_api_base=os.getenv("OPENAI_BASE_URL"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
        )
        e = QAEnhance(req)

        qa = e.generate_qa()
        logger.info(qa)
