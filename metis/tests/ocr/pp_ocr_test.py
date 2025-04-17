from src.ocr.pp_ocr import PPOcr


def test_pp_ocr():
    ocr = PPOcr()
    print(ocr.predict('./tests/assert/umr.jpeg'))
