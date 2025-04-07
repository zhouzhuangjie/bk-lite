import uuid

from pydantic import BaseModel
from sanic import Blueprint, json
import tempfile
import os

from sanic_ext import validate

from src.chunk.fixed_size_chunk import FixedSizeChunk
from src.loader.text_loader import TextLoader
from src.rag.native_rag.entity.elasticsearch_store_request import ElasticSearchStoreRequest
from src.rag.native_rag.rag.elasticsearch_rag import ElasticSearchRag

rag_api_router = Blueprint("rag", url_prefix="/rag")


@rag_api_router.post("/ingest")
async def ingest(request):
    # 获取文件和知识库索引名称
    file = request.files.get('file')
    allowed_types = ['docx', 'pptx', 'ppt', 'doc', 'txt', 'jpg', 'png', 'jpeg']
    file_extension = file.name.split('.')[-1].lower() if '.' in file.name else ''

    if file_extension not in allowed_types:
        return json({"status": "error", "message": f"Unsupported file type. Allowed types: {', '.join(allowed_types)}"})

    index_name = request.form.get('index_name')
    knowledge_id = request.form.get('knowledge_id')
    embed_model_base_url = request.form.get('embed_model_base_url')
    embed_model_api_key = request.form.get('embed_model_api_key')
    embed_model_name = request.form.get('embed_model_name')

    try:
        with tempfile.NamedTemporaryFile(delete=True, suffix=f'.{file_extension}') as temp_file:
            temp_file.write(file.body)
            temp_file.flush()
            temp_path = temp_file.name

            if file_extension == 'txt':
                loader = TextLoader(temp_path)

            docs = loader.load()
            for doc in docs:
                doc.metadata['knowledge_title'] = file.name
                doc.metadata['knowledge_id'] = knowledge_id
                doc.metadata['chunk_id'] = str(uuid.uuid4())

            chunk_mode = request.form.get('chunk_mode')
            if chunk_mode == 'fixed_size':
                chunk_size = int(request.form.get('chunk_size'))
                chunk = FixedSizeChunk(chunk_size=chunk_size)

            docs = chunk.chunk(docs)

            elasticsearch_store_request = ElasticSearchStoreRequest(
                index_name=index_name,
                docs=docs,
                embed_model_base_url=embed_model_base_url,
                embed_model_api_key=embed_model_api_key,
                embed_model_name=embed_model_name
            )
            rag = ElasticSearchRag()
            rag.ingest(elasticsearch_store_request)

        return json({"status": "success", "message": ""})
    except Exception as e:
        return json({"status": "error", "message": str(e)})


@rag_api_router.get("/delete_index")
async def delete_index(request):
    """
    删除知识库
    :param request:
    :return:
    """
    pass


@rag_api_router.post("/delete_doc")
async def delete_doc(request):
    """
    删除知识文档
    :param request:
    :return:
    """
    pass


@rag_api_router.post("/rag_test")
async def rag_test(request):
    """
    查询测试
    :param request:
    :return:
    """
    pass
