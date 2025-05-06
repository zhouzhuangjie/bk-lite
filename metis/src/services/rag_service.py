import uuid
from typing import Optional

from langchain_openai import OpenAIEmbeddings
from loguru import logger

from src.chunk.fixed_size_chunk import FixedSizeChunk
from src.chunk.full_chunk import FullChunk
from src.chunk.recursive_chunk import RecursiveChunk
from src.chunk.semantic_chunk import SemanticChunk
from src.loader.doc_loader import DocLoader
from src.loader.excel_loader import ExcelLoader
from src.loader.image_loader import ImageLoader
from src.loader.markdown_loader import MarkdownLoader
from src.loader.pdf_loader import PDFLoader
from src.loader.ppt_loader import PPTLoader
from src.loader.text_loader import TextLoader
from src.ocr.azure_ocr import AzureOCR
from src.ocr.olm_ocr import OlmOcr
from src.ocr.pp_ocr import PPOcr


class RagService:
    @classmethod
    def serialize_documents(cls, docs):
        """
        将文档序列化为JSON格式
        """
        logger.debug(f"序列化 {len(docs)} 个文档")
        serialized_docs = []
        for doc in docs:
            serialized_docs.append({
                "page_content": doc.page_content,
                "metadata": doc.metadata
            })
        return serialized_docs

    @classmethod
    def process_documents(cls, docs, knowledge_title, knowledge_id=None):
        """
        处理文档，添加元数据
        """
        logger.debug(f"处理文档元数据，标题: {knowledge_title}, ID: {knowledge_id}, 文档数量: {len(docs)}")
        for index, doc in enumerate(docs):
            doc.metadata['knowledge_title'] = knowledge_title
            if knowledge_id:
                doc.metadata['knowledge_id'] = knowledge_id
            doc.metadata['segment_id'] = str(uuid.uuid4())
            doc.metadata['segment_number'] = index
        return docs

    @classmethod
    def get_chunker(cls, chunk_mode, request=None):
        """
        根据分块模式返回相应的分块器
        """
        logger.debug(f"初始化分块器，模式: {chunk_mode}")
        if chunk_mode == 'fixed_size':
            chunk_size = int(request.form.get('chunk_size', 256))
            logger.debug(f"使用固定大小分块，大小: {chunk_size}")
            return FixedSizeChunk(chunk_size=chunk_size)

        elif chunk_mode == 'full':
            logger.debug("使用全文分块")
            return FullChunk()

        elif chunk_mode == 'recursive':
            chunk_size = int(request.form.get('chunk_size', 256))
            chunk_overlap = int(request.form.get('chunk_overlap', 128))
            logger.debug(f"使用递归分块，大小: {chunk_size}, 重叠: {chunk_overlap}")
            return RecursiveChunk(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

        elif chunk_mode == 'semantic':
            semantic_chunk_model = request.form.get('semantic_chunk_model')
            semantic_chunk_model_base_url = request.form.get(
                'semantic_chunk_model_base_url')
            logger.debug(f"使用语义分块，模型: {semantic_chunk_model}, URL: {semantic_chunk_model_base_url}")
            semantic_chunk_model_api_key = request.form.get(
                'semantic_chunk_model_api_key')
            embeddings = OpenAIEmbeddings(
                model=semantic_chunk_model,
                api_key=semantic_chunk_model_api_key,
                base_url=semantic_chunk_model_base_url,
            )
            return SemanticChunk(embeddings)
        else:
            error_msg = f"不支持的分块模式: {chunk_mode}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    @classmethod
    def get_file_loader(cls, file_path, file_extension, load_mode, request=None):
        """
        根据文件类型选择适当的加载器
        在内部初始化OCR，支持paddle_ocr、olm_ocr、azure_ocr
        """
        logger.debug(f"为文件 {file_path} (类型: {file_extension}) 初始化加载器")
        # 初始化OCR
        ocr = None
        ocr = cls.load_ocr(request)
        if ocr:
            logger.debug(f"OCR类型: {type(ocr).__name__} 初始化成功")

        if file_extension in ['docx', 'doc']:
            return DocLoader(file_path, ocr, load_mode)
        elif file_extension in ['pptx', 'ppt']:
            return PPTLoader(file_path, load_mode)
        elif file_extension == 'txt':
            return TextLoader(file_path, load_mode)
        elif file_extension in ['jpg', 'png', 'jpeg']:
            return ImageLoader(file_path, ocr, load_mode)
        elif file_extension == 'pdf':
            return PDFLoader(file_path, ocr, load_mode)
        elif file_extension in ['xlsx', 'xls', 'csv']:
            return ExcelLoader(file_path, load_mode)
        elif file_extension in ['md']:
            return MarkdownLoader(file_path, load_mode)
        else:
            raise ValueError(f"不支持的文件类型: {file_extension}")

    @classmethod
    def load_ocr(cls, ocr_type: str,
                 olm_base_url: Optional[str], olm_api_key: Optional[str], olm_model: Optional[str],
                 azure_base_url: Optional[str], azure_api_key: Optional[str]):
        ocr = None
        logger.debug(f"加载OCR服务，类型: {ocr_type}")

        if ocr_type == 'pp_ocr':
            logger.debug("初始化PP-OCR服务")
            ocr = PPOcr()

        if ocr_type == 'olm_ocr':
            logger.debug(f"初始化OLM-OCR服务，模型: {olm_model}")
            ocr = OlmOcr(base_url=olm_base_url, api_key=olm_api_key, model=olm_model)

        if ocr_type == 'azure_ocr':
            logger.debug(f"初始化Azure-OCR服务，endpoint: {azure_base_url}")
            ocr = AzureOCR(api_key=azure_api_key, endpoint=azure_base_url)

        return ocr
