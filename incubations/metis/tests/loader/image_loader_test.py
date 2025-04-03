from src.loader.image_loader import ImageLoader
from src.ocr.pp_ocr import PPOcr


def test_image_loader():
    loader = ImageLoader('../assert/umr.jpeg', PPOcr())
    print(loader.load())
