import paddle
from paddleocr import PaddleOCR

from src.ocr.base_ocr import BaseOCR


class PPOcr(BaseOCR):
    def __init__(self):
        gpu_available = paddle.device.is_compiled_with_cuda()
        self.ocr_engine = PaddleOCR(table=True, show_log=True, lang='ch', use_angle_cls=True, use_gpu=gpu_available)

    def predict(self, file):
        result = self.ocr_engine.ocr(file, cls=True)
        recognized_texts = ''
        if result:
            for lines in result:
                for line in lines:
                    recognized_texts += line[1][0] + ''
        return recognized_texts
