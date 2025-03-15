import base64
import tempfile
import os
from typing import List
from loguru import logger
from langchain_core.documents import Document

from core.user_types.ocr_request import OcrRequest


class OcrRunnable:
    def predict(self, file_path: str) -> List[Document]:
        pass

    def execute(self, request: OcrRequest) -> List[Document]:
        base_image = base64.b64decode(request.file)

        # 使用临时文件保存图像数据
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(base_image)

        try:
            result = self.predict(temp_file_path)
            return result
        except Exception as e:
            logger.error("OCR failed: ", e)
            return []
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
