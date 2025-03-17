import base64
import os
import tempfile
from typing import List

import paddle
from langchain_core.documents import Document
from langchain_core.runnables import RunnableLambda
from langserve import add_routes
from loguru import logger
from paddleocr import PaddleOCR

from core.user_types.ocr_request import OcrRequest


class PaddleOcrRunnable():
    def __init__(self):
        gpu_available = paddle.device.is_compiled_with_cuda()
        self.ocr_engine = PaddleOCR(table=True, show_log=True, lang='ch', use_angle_cls=True, use_gpu=gpu_available)

    def predict(self, request: OcrRequest) -> List[Document]:
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            try:
                base_image = base64.b64decode(request.file)
                temp_file.write(base_image)
                temp_file.flush()

                result = self.ocr_engine.ocr(temp_file.name, cls=True)
                recognized_texts = ''
                if result:
                    for lines in result:
                        for line in lines:
                            recognized_texts += line[1][0] + ''

                return [Document(page_content=recognized_texts)]
            except Exception as e:
                logger.warning(f"Failed to recognize text: {e}")
                return []
            finally:
                temp_file.close()
                os.unlink(temp_file.name)

    def register(self, app):
        add_routes(app,
                   RunnableLambda(self.predict).with_types(input_type=OcrRequest, output_type=List[Document]),
                   path='/paddle_ocr')
