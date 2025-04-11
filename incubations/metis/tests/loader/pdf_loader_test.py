from src.loader.pdf_loader import PDFLoader
from src.ocr.pp_ocr import PPOcr
import json  # 添加导入 json 模块


def test_load_pdf():
    ocr = PPOcr()
    loader = PDFLoader(file_path="tests/assert/pdf_word_raw.pdf", ocr=ocr)
    print(loader.load())
