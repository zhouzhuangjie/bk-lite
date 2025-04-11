import uuid

from sanic import Blueprint, json
import tempfile
import os

from sanic_ext import validate
from src.loader.doc_loader import DocLoader
from src.loader.excel_loader import ExcelLoader
from src.chunk.fixed_size_chunk import FixedSizeChunk
from src.core.web.api_auth import auth
from src.loader.image_loader import ImageLoader
from src.loader.markdown_loader import MarkdownLoader
from src.loader.pdf_loader import PDFLoader
from src.loader.ppt_loader import PPTLoader
from src.loader.raw_loader import RawLoader
from src.loader.text_loader import TextLoader
from src.loader.website_loader import WebSiteLoader
from src.rag.native_rag.entity.elasticsearch_document_count_request import ElasticSearchDocumentCountRequest
from src.rag.native_rag.entity.elasticsearch_document_delete_request import ElasticSearchDocumentDeleteRequest
from src.rag.native_rag.entity.elasticsearch_document_list_request import ElasticSearchDocumentListRequest
from src.rag.native_rag.entity.elasticsearch_index_delete_request import ElasticSearchIndexDeleteRequest
from src.rag.native_rag.entity.elasticsearch_store_request import ElasticSearchStoreRequest
from src.rag.native_rag.rag.elasticsearch_rag import ElasticSearchRag
from sanic.log import logger

rag_api_router = Blueprint("rag", url_prefix="/rag")


@rag_api_router.post("/count_index_document")
@auth.login_required
@validate(json=ElasticSearchDocumentCountRequest)
async def count_index_document(request, body: ElasticSearchDocumentCountRequest):
    try:
        rag = ElasticSearchRag()
        count = rag.count_index_document(body)
        return json({"status": "success", "message": "", "count": count})
    except Exception as e:
        return json({"status": "error", "message": str(e)})


@rag_api_router.post("/cusom_content_ingest")
@auth.login_required
async def cusom_content_ingest(request):
    knowledge_base_id = request.form.get('knowledge_base_id')
    knowledge_id = request.form.get('knowledge_id')
    embed_model_base_url = request.form.get('embed_model_base_url')
    embed_model_api_key = request.form.get('embed_model_api_key')
    embed_model_name = request.form.get('embed_model_name')
    chunk_mode = request.form.get('chunk_mode')
    chunk_size = int(request.form.get('chunk_size', 1000))
    content = request.form.get('content')

    loader = RawLoader(content)
    docs = loader.load()
    for doc in docs:
        doc.metadata['knowledge_title'] = knowledge_id
        doc.metadata['knowledge_id'] = knowledge_id
        doc.metadata['chunk_id'] = str(uuid.uuid4())
    chunk = None
    if chunk_mode == 'fixed_size':
        chunk = FixedSizeChunk(chunk_size=chunk_size)
    docs = chunk.chunk(docs)
    elasticsearch_store_request = ElasticSearchStoreRequest(
        index_name=knowledge_base_id,
        docs=docs,
        embed_model_base_url=embed_model_base_url,
        embed_model_api_key=embed_model_api_key,
        embed_model_name=embed_model_name
    )
    rag = ElasticSearchRag()
    rag.ingest(elasticsearch_store_request)
    return json({"status": "success", "message": ""})


@rag_api_router.post("/website_ingest")
@auth.login_required
async def website_ingest(request):
    knowledge_base_id = request.form.get('knowledge_base_id')
    knowledge_id = request.form.get('knowledge_id')
    embed_model_base_url = request.form.get('embed_model_base_url')
    embed_model_api_key = request.form.get('embed_model_api_key')
    embed_model_name = request.form.get('embed_model_name')

    url = request.form.get('url')
    max_depth = int(request.form.get('max_depth', 1))
    chunk_mode = request.form.get('chunk_mode')
    chunk_size = int(request.form.get('chunk_size', 1000))
    load_mode = request.form.get('load_mode')

    loader = WebSiteLoader(url, max_depth)
    docs = loader.load()
    for doc in docs:
        doc.metadata['knowledge_title'] = url
        doc.metadata['knowledge_id'] = knowledge_id
        doc.metadata['chunk_id'] = str(uuid.uuid4())
    chunk = None
    if chunk_mode == 'fixed_size':
        chunk = FixedSizeChunk(chunk_size=chunk_size)
    docs = chunk.chunk(docs)
    elasticsearch_store_request = ElasticSearchStoreRequest(
        index_name=knowledge_base_id,
        docs=docs,
        embed_model_base_url=embed_model_base_url,
        embed_model_api_key=embed_model_api_key,
        embed_model_name=embed_model_name
    )
    rag = ElasticSearchRag()
    rag.ingest(elasticsearch_store_request)
    return json({"status": "success", "message": ""})


@rag_api_router.post("/file_ingest")
@auth.login_required
async def file_ingest(request):
    file = request.files.get('file')
    allowed_types = ['docx', 'pptx', 'ppt', 'doc', 'txt',
                     'jpg', 'png', 'jpeg', 'pdf', 'csv', 'xlsx', 'xls', 'md']
    file_extension = file.name.split(
        '.')[-1].lower() if '.' in file.name else ''

    if file_extension not in allowed_types:
        return json({"status": "error", "message": f"Unsupported file type. Allowed types: {', '.join(allowed_types)}"})

    knowledge_base_id = request.form.get('knowledge_base_id')
    knowledge_id = request.form.get('knowledge_id')
    embed_model_base_url = request.form.get('embed_model_base_url')
    embed_model_api_key = request.form.get('embed_model_api_key')
    embed_model_name = request.form.get('embed_model_name')

    ocr = None
    try:
        with tempfile.NamedTemporaryFile(delete=True, suffix=f'.{file_extension}') as temp_file:
            temp_file.write(file.body)
            temp_file.flush()
            temp_path = temp_file.name

            logger.info(f'处理文件：{temp_path}')
            if file_extension in ['docx', 'doc']:
                loader = DocLoader(temp_path, ocr)
            if file_extension in ['pptx', 'ppt']:
                loader = PPTLoader(temp_path)
            if file_extension == 'txt':
                loader = TextLoader(temp_path)
            if file_extension in ['jpg', 'png', 'jpeg']:
                loader = ImageLoader(temp_path, ocr)
            if file_extension == 'pdf':
                loader = PDFLoader(temp_path, ocr)
            if file_extension in ['xlsx', 'xls', 'csv']:
                loader = ExcelLoader(temp_path)
            if file_extension in ['md']:
                loader = MarkdownLoader(temp_path)

            docs = loader.load()
            for doc in docs:
                doc.metadata['knowledge_title'] = file.name
                doc.metadata['knowledge_id'] = knowledge_id
                doc.metadata['chunk_id'] = str(uuid.uuid4())

            chunk_mode = request.form.get('chunk_mode')
            logger.info(f'文档解析模式：{chunk_mode}')
            if chunk_mode == 'fixed_size':
                chunk_size = int(request.form.get('chunk_size'))
                chunk = FixedSizeChunk(chunk_size=chunk_size)

            docs = chunk.chunk(docs)

            elasticsearch_store_request = ElasticSearchStoreRequest(
                index_name=knowledge_base_id,
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


@rag_api_router.post("/delete_index")
@validate(json=ElasticSearchIndexDeleteRequest)
@auth.login_required
async def delete_index(request, body: ElasticSearchIndexDeleteRequest):
    try:
        rag = ElasticSearchRag()
        rag.delete_index(body)
        return json({"status": "success", "message": ""})
    except Exception as e:
        return json({"status": "error", "message": str(e)})


@rag_api_router.post("/delete_doc")
@auth.login_required
@validate(json=ElasticSearchDocumentDeleteRequest)
async def delete_doc(request, body: ElasticSearchDocumentDeleteRequest):
    """
    删除文档
    :param request:
    :param body:
    :return:
    """
    rag = ElasticSearchRag()
    rag.delete_document(body)
    return json({"status": "success", "message": ""})


@rag_api_router.post("/file_chunk_preview")
@auth.login_required
async def file_chunk_preview(request):
    """
    分块预览
    :param request: 包含文件和分块参数的请求
    :return: 返回分块后的文档内容，但不写入ES
    """
    file = request.files.get('file')
    allowed_types = ['docx', 'pptx', 'ppt', 'doc', 'txt',
                     'jpg', 'png', 'jpeg', 'pdf', 'csv', 'xlsx', 'xls', 'md']
    file_extension = file.name.split(
        '.')[-1].lower() if '.' in file.name else ''

    if file_extension not in allowed_types:
        return json({"status": "error", "message": f"Unsupported file type. Allowed types: {', '.join(allowed_types)}"})

    knowledge_id = request.form.get('knowledge_id')

    ocr = None
    try:
        with tempfile.NamedTemporaryFile(delete=True, suffix=f'.{file_extension}') as temp_file:
            temp_file.write(file.body)
            temp_file.flush()
            temp_path = temp_file.name

            logger.info(f'预览分块文件：{temp_path}')

            # 根据文件类型选择适当的加载器
            if file_extension in ['docx', 'doc']:
                loader = DocLoader(temp_path, ocr)
            elif file_extension in ['pptx', 'ppt']:
                loader = PPTLoader(temp_path)
            elif file_extension == 'txt':
                loader = TextLoader(temp_path)
            elif file_extension in ['jpg', 'png', 'jpeg']:
                loader = ImageLoader(temp_path, ocr)
            elif file_extension == 'pdf':
                loader = PDFLoader(temp_path, ocr)
            elif file_extension in ['xlsx', 'xls', 'csv']:
                loader = ExcelLoader(temp_path)
            elif file_extension in ['md']:
                loader = MarkdownLoader(temp_path)

            docs = loader.load()
            for doc in docs:
                doc.metadata['knowledge_title'] = file.name
                doc.metadata['knowledge_id'] = knowledge_id
                doc.metadata['chunk_id'] = str(uuid.uuid4())

            chunk_mode = request.form.get('chunk_mode')
            logger.info(f'文档分块预览模式：{chunk_mode}')
            if chunk_mode == 'fixed_size':
                chunk_size = int(request.form.get('chunk_size', 1000))
                chunk = FixedSizeChunk(chunk_size=chunk_size)
                docs = chunk.chunk(docs)

            # 转换文档为可JSON序列化格式
            serialized_docs = []
            for doc in docs:
                serialized_docs.append({
                    "page_content": doc.page_content,
                    "metadata": doc.metadata
                })

            return json({
                "status": "success",
                "message": "",
                "documents": serialized_docs
            })
    except Exception as e:
        logger.error(f"文件分块预览错误: {str(e)}")
        return json({"status": "error", "message": str(e)})


@rag_api_router.post("/list_rag_document")
@auth.login_required
@validate(json=ElasticSearchDocumentListRequest)
async def list_rag_document(request, body: ElasticSearchDocumentListRequest):
    """
    查询RAG数据
    :param request:
    :param body:
    :return:
    """
    try:
        rag = ElasticSearchRag()
        documents = rag.list_index_document(body)
        return json({"status": "success", "message": "", "documents": [doc.dict() for doc in documents]})
    except Exception as e:
        return json({"status": "error", "message": str(e)})
