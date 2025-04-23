import traceback
import uuid

from langchain_openai import OpenAIEmbeddings
from sanic import Blueprint, json
import tempfile
import os
import json as js
from sanic_ext import validate
from src.chunk.full_chunk import FullChunk
from src.chunk.semantic_chunk import SemanticChunk
from src.chunk.recursive_chunk import RecursiveChunk
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
from src.ocr.azure_ocr import AzureOCR
from src.ocr.olm_ocr import OlmOcr
from src.ocr.pp_ocr import PPOcr
from src.rag.native_rag.entity.elasticsearch_document_count_request import ElasticSearchDocumentCountRequest
from src.rag.native_rag.entity.elasticsearch_document_delete_request import ElasticSearchDocumentDeleteRequest
from src.rag.native_rag.entity.elasticsearch_document_list_request import ElasticSearchDocumentListRequest
from src.rag.native_rag.entity.elasticsearch_document_metadata_update_request import \
    ElasticsearchDocumentMetadataUpdateRequest
from src.rag.native_rag.entity.elasticsearch_index_delete_request import ElasticSearchIndexDeleteRequest
from src.rag.native_rag.entity.elasticsearch_retriever_request import ElasticSearchRetrieverRequest
from src.rag.native_rag.entity.elasticsearch_store_request import ElasticSearchStoreRequest
from src.rag.native_rag.rag.elasticsearch_rag import ElasticSearchRag
from sanic.log import logger

rag_api_router = Blueprint("rag", url_prefix="/rag")


def get_file_loader(file_path, file_extension, request=None):
    """
    根据文件类型选择适当的加载器
    在内部初始化OCR，支持paddle_ocr、olm_ocr、azure_ocr
    """
    # 初始化OCR
    ocr = None
    ocr = load_ocr(ocr, request)

    if file_extension in ['docx', 'doc']:
        return DocLoader(file_path, ocr)
    elif file_extension in ['pptx', 'ppt']:
        return PPTLoader(file_path)
    elif file_extension == 'txt':
        return TextLoader(file_path)
    elif file_extension in ['jpg', 'png', 'jpeg']:
        return ImageLoader(file_path, ocr)
    elif file_extension == 'pdf':
        return PDFLoader(file_path, ocr)
    elif file_extension in ['xlsx', 'xls', 'csv']:
        return ExcelLoader(file_path)
    elif file_extension in ['md']:
        return MarkdownLoader(file_path)
    else:
        raise ValueError(f"不支持的文件类型: {file_extension}")


def load_ocr(ocr, request):
    ocr = None
    ocr_type = request.form.get('ocr_type')

    if ocr_type == 'pp_ocr':
        ocr = PPOcr()

    if ocr_type == 'olm_ocr':
        base_url = request.form.get('olm_base_url')
        api_key = request.form.get('olm_api_key')
        model = request.form.get(
            'olm_model', "allenai/olmOCR-7B-0225-preview")
        ocr = OlmOcr(base_url=base_url, api_key=api_key, model=model)

    if ocr_type == 'azure_ocr':
        azure_api_key = request.form.get('azure_api_key')
        azure_endpoint = request.form.get('azure_endpoint')
        ocr = AzureOCR(api_key=azure_api_key, endpoint=azure_endpoint)

    return ocr


def get_chunker(chunk_mode, request=None):
    """
    根据分块模式返回相应的分块器
    """
    if chunk_mode == 'fixed_size':
        chunk_size = int(request.form.get('chunk_size', 256))
        return FixedSizeChunk(chunk_size=chunk_size)

    elif chunk_mode == 'full':
        return FullChunk()

    elif chunk_mode == 'recursive':
        chunk_size = int(request.form.get('chunk_size', 256))
        chunk_overlap = int(request.form.get('chunk_overlap', 128))
        return RecursiveChunk(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    elif chunk_mode == 'semantic':
        semantic_chunk_model = request.form.get('semantic_chunk_model')
        semantic_chunk_model_base_url = request.form.get(
            'semantic_chunk_model_base_url')
        semantic_chunk_model_api_key = request.form.get(
            'semantic_chunk_model_api_key')
        embeddings = OpenAIEmbeddings(
            model=semantic_chunk_model,
            api_key=semantic_chunk_model_api_key,
            base_url=semantic_chunk_model_base_url,
        )
        return SemanticChunk(embeddings)
    else:
        raise ValueError(f"不支持的分块模式: {chunk_mode}")


def process_documents(docs, knowledge_title, knowledge_id=None):
    """
    处理文档，添加元数据
    """
    for doc in docs:
        doc.metadata['knowledge_title'] = knowledge_title
        if knowledge_id:
            doc.metadata['knowledge_id'] = knowledge_id
        doc.metadata['chunk_id'] = str(uuid.uuid4())
    return docs


def serialize_documents(docs):
    """
    将文档序列化为JSON格式
    """
    serialized_docs = []
    for doc in docs:
        serialized_docs.append({
            "page_content": doc.page_content,
            "metadata": doc.metadata
        })
    return serialized_docs


@rag_api_router.post("/naive_rag_test")
@auth.login_required
@validate(json=ElasticSearchRetrieverRequest)
def naive_rag_test(request, body: ElasticSearchRetrieverRequest):
    """
    测试RAG
    :param request:
    :param body:
    :return:
    """
    try:
        rag = ElasticSearchRag()
        documents = rag.search(body)
        return json({"status": "success", "message": "", "documents": [doc.dict() for doc in documents]})
    except Exception as e:
        traceback.print_exc()
        return json({"status": "error", "message": str(e)})


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


@rag_api_router.post("/custom_content_ingest")
@auth.login_required
async def custom_content_ingest(request):
    try:
        content = request.form.get('content')
        chunk_mode = request.form.get('chunk_mode')
        is_preview = request.form.get('preview', 'false').lower() == 'true'
        metadata = js.loads(request.form.get('metadata','{}'))
        # 加载自定义内容
        loader = RawLoader(content)
        docs = loader.load()

        # 处理文档元数据
        docs = prepare_documents_metadata(docs,
                                          is_preview=is_preview,
                                          title="自定义内容",
                                          knowledge_id=request.form.get('knowledge_id'))
        # 执行文档分块
        chunker = get_chunker(chunk_mode, request)
        chunked_docs = chunker.chunk(docs)

        # 处理预览模式
        if is_preview:
            return json({
                "status": "success",
                "message": "",
                "documents": serialize_documents(chunked_docs)
            })

        # 执行文档存储
        store_documents_to_es(
            chunked_docs=chunked_docs,
            knowledge_base_id=request.form.get('knowledge_base_id'),
            embed_model_base_url=request.form.get('embed_model_base_url'),
            embed_model_api_key=request.form.get('embed_model_api_key'),
            embed_model_name=request.form.get('embed_model_name'),
            metadata=metadata
        )

        return json({"status": "success", "message": ""})
    except Exception as e:
        logger.error(f"自定义内容处理错误: {str(e)}")
        return json({"status": "error", "message": str(e)})


@rag_api_router.post("/website_ingest")
@auth.login_required
async def website_ingest(request):
    try:
        url = request.form.get('url')
        max_depth = int(request.form.get('max_depth', 1))
        chunk_mode = request.form.get('chunk_mode')
        is_preview = request.form.get('preview', 'false').lower() == 'true'
        metadata = js.loads(request.form.get('metadata','{}'))

        # 加载网站内容
        loader = WebSiteLoader(url, max_depth)
        docs = loader.load()

        # 处理文档元数据
        docs = prepare_documents_metadata(docs,
                                          is_preview=is_preview,
                                          title=url,
                                          knowledge_id=request.form.get('knowledge_id'))

        # 执行文档分块并记录日志
        chunked_docs = perform_chunking(
            docs, chunk_mode, request, is_preview, "网站内容")

        # 处理预览模式
        if is_preview:
            return json({
                "status": "success",
                "message": "",
                "documents": serialize_documents(chunked_docs)
            })

        # 执行文档存储
        store_documents_to_es(
            chunked_docs=chunked_docs,
            knowledge_base_id=request.form.get('knowledge_base_id'),
            embed_model_base_url=request.form.get('embed_model_base_url'),
            embed_model_api_key=request.form.get('embed_model_api_key'),
            embed_model_name=request.form.get('embed_model_name'),
            metadata=metadata
        )

        return json({"status": "success", "message": ""})
    except Exception as e:
        logger.error(f"网站内容处理错误: {str(e)}")
        return json({"status": "error", "message": str(e)})


@rag_api_router.post("/file_ingest")
@auth.login_required
async def file_ingest(request):
    file = request.files.get('file')
    logger.info(f"上传文件名: {file.name}, 文件大小: {len(file.body) / (1024 * 1024):.2f} MB")
    allowed_types = ['docx', 'pptx', 'ppt', 'doc', 'txt',
                     'jpg', 'png', 'jpeg', 'pdf', 'csv', 'xlsx', 'xls', 'md']
    file_extension = file.name.split(
        '.')[-1].lower() if '.' in file.name else ''

    if file_extension not in allowed_types:
        return json({"status": "error", "message": f"不支持的文件类型。支持的类型: {', '.join(allowed_types)}"})

    is_preview = request.form.get('preview', 'false').lower() == 'true'
    chunk_mode = request.form.get('chunk_mode')
    metadata = js.loads(request.form.get('metadata','{}'))

    try:
        with tempfile.NamedTemporaryFile(delete=True, suffix=f'.{file_extension}') as temp_file:
            temp_file.write(file.body)
            temp_file.flush()
            temp_path = temp_file.name

            # 日志记录
            operation_type = "预览分块文件" if is_preview else "处理文件"
            logger.info(f'{operation_type}：{temp_path}')

            # 加载文件内容
            loader = get_file_loader(temp_path, file_extension, request)
            docs = loader.load()

            # 处理文档元数据
            docs = prepare_documents_metadata(docs,
                                              is_preview=is_preview,
                                              title=file.name,
                                              knowledge_id=request.form.get('knowledge_id'))

            # 执行文档分块并记录日志
            chunked_docs = perform_chunking(
                docs, chunk_mode, request, is_preview, "文件内容")

            # 处理预览模式
            if is_preview:
                return json({
                    "status": "success",
                    "message": "",
                    "documents": serialize_documents(chunked_docs)
                })

            # 执行文档存储
            store_documents_to_es(
                chunked_docs=chunked_docs,
                knowledge_base_id=request.form.get('knowledge_base_id'),
                embed_model_base_url=request.form.get('embed_model_base_url'),
                embed_model_api_key=request.form.get('embed_model_api_key'),
                embed_model_name=request.form.get('embed_model_name'),
                metadata=metadata
            )

        return json({"status": "success", "message": ""})
    except Exception as e:
        logger.error(f"文件处理错误: {str(e)}")
        return json({"status": "error", "message": str(e)})


# 添加以下辅助函数，使代码更加模块化和易于维护

def prepare_documents_metadata(docs, is_preview, title, knowledge_id=None):
    """
    准备文档的元数据

    Args:
        docs: 文档列表
        is_preview: 是否为预览模式
        title: 文档标题
        knowledge_id: 知识库ID，预览模式下不需要

    Returns:
        处理后的文档列表
    """
    if is_preview:
        return process_documents(docs, title)
    else:
        return process_documents(docs, title, knowledge_id)


def perform_chunking(docs, chunk_mode, request, is_preview, content_type):
    """
    执行文档分块并记录相关日志

    Args:
        docs: 文档列表
        chunk_mode: 分块模式
        request: HTTP请求对象
        is_preview: 是否为预览模式
        content_type: 内容类型

    Returns:
        分块后的文档列表
    """
    if is_preview:
        logger.info(f'{content_type}分块预览模式：{chunk_mode}')

    chunker = get_chunker(chunk_mode, request)
    return chunker.chunk(docs)


def store_documents_to_es(chunked_docs, knowledge_base_id, embed_model_base_url,
                          embed_model_api_key, embed_model_name, metadata={}):
    """
    将文档存储到ElasticSearch

    Args:
        chunked_docs: 分块后的文档
        knowledge_base_id: 知识库ID
        embed_model_base_url: 嵌入模型基础URL
        embed_model_api_key: 嵌入模型API密钥
        embed_model_name: 嵌入模型名称
    """
    if metadata:
        for doc in chunked_docs:
            doc.metadata.update(metadata)

    elasticsearch_store_request = ElasticSearchStoreRequest(
        index_name=knowledge_base_id,
        docs=chunked_docs,
        embed_model_base_url=embed_model_base_url,
        embed_model_api_key=embed_model_api_key,
        embed_model_name=embed_model_name,
    )
    rag = ElasticSearchRag()
    rag.ingest(elasticsearch_store_request)


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

@rag_api_router.post("/update_rag_document_metadata")
@auth.login_required
@validate(json=ElasticsearchDocumentMetadataUpdateRequest)
async def update_rag_document_metadata(request, body: ElasticsearchDocumentMetadataUpdateRequest):
    try:
        rag = ElasticSearchRag()
        rag.update_metadata(body)
        return json({"status": "success", "message": "文档元数据更新成功"})
    except Exception as e:
        logger.error(f"更新文档元数据错误: {str(e)}")
        return json({"status": "error", "message": str(e)})