

import os

from dotenv import load_dotenv
from src.ocr.olm_ocr import OlmOcr

load_dotenv()


def test_olm_ocr():
    ocr = OlmOcr(base_url=os.getenv('TEST_INFERENCE_BASE_URL'),
                 api_key=os.getenv('TEST_INFERENCE_TOKEN'))

    print(ocr.predict('./tests/assert/umr.jpeg'))
