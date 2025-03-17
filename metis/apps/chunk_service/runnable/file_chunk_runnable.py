import base64
import os
import tempfile
from typing import List

from langchain_core.documents import Document
from langchain_core.runnables import RunnableLambda
from langserve import add_routes
from loguru import logger

from apps.chunk_service.loader.doc_loader import DocLoader
from apps.chunk_service.loader.excel_loader import ExcelLoader
from apps.chunk_service.loader.image_loader import ImageLoader
from apps.chunk_service.loader.pdf_loader import PDFLoader
from apps.chunk_service.loader.ppt_loader import PPTLoader
from apps.chunk_service.loader.text_loader import TextLoader
from apps.chunk_service.runnable.base_chunk_runnable import BaseChunkRunnable
from apps.chunk_service.user_types.file_chunk_request import FileChunkRequest


class FileChunkRunnable(BaseChunkRunnable):
    def __init__(self):
        pass

    def parse(self, request: FileChunkRequest) -> List[Document]:
        try:
            content = base64.b64decode(request.file.encode("utf-8"))
            file_name, file_type = os.path.splitext(request.file_name)
            logger.debug(f"待处理文件名：{file_name}, 文件类型：{file_type}")

            pure_filename = file_name.split("/")[-1]

            if file_type == ".txt":
                return self._handle_text_file(content, file_name, request)
            else:
                return self._handle_other_file_types(content, file_type, pure_filename, request)
        except Exception as e:
            logger.error(f"解析文件失败: {e}")
            return []

    def _handle_text_file(self, content: bytes, file_name: str, request: FileChunkRequest) -> List[Document]:
        try:
            logger.debug(f"[{file_name}]格式为文本文件，尝试使用 utf-8 解码")
            text_content = content.decode('utf-8')
        except UnicodeDecodeError:
            logger.warning(f"utf-8 解码失败，尝试使用 gbk 解码")
            text_content = content.decode('gbk')

        with tempfile.NamedTemporaryFile(delete=True) as f:
            f.write(text_content.encode())
            f.flush()
            loader = TextLoader(f.name)
            return self.parse_docs(loader.load(), request)

    def _handle_other_file_types(self, content: bytes, file_type: str, pure_filename: str, request: FileChunkRequest) -> \
            List[Document]:
        with tempfile.NamedTemporaryFile(delete=True) as f:
            f.write(content)
            f.flush()
            loader = self._get_loader_by_file_type(f.name, file_type, request)
            docs = loader.load()
            return self.parse_docs(docs, request)

    def _get_loader_by_file_type(self, file_path: str, file_type: str, request: FileChunkRequest):
        if file_type == ".md":
            return TextLoader(file_path)
        if file_type in [".ppt", ".pptx"]:
            return PPTLoader(file_path)
        elif file_type == ".pdf":
            return PDFLoader(file_path, request.ocr_provider_address, request.enable_ocr_parse)
        elif file_type in [".doc", ".docx"]:
            return DocLoader(file_path, request.ocr_provider_address, request.enable_ocr_parse)
        elif file_type in [".xls", ".xlsx"]:
            return ExcelLoader(file_path, request)
        elif file_type in [".jpg", ".png", ".jpeg"]:
            return ImageLoader(file_path, request)
        else:
            raise ValueError(f"不支持的文件类型: {file_type}")

    def register(self, app):
        add_routes(app,
                   RunnableLambda(self.parse).with_types(input_type=FileChunkRequest, output_type=List[Document]),
                   path='/file_chunk')
