from dotenv import load_dotenv

from src.chunk.fixed_size_chunk import FixedSizeChunk
from src.loader.text_loader import TextLoader

load_dotenv()


def test_fixed_size_chunk():

    chunk = FixedSizeChunk()
    loader = TextLoader(path='../assert/full_text_loader.txt')
    docs = loader.load()
    rs = chunk.chunk(docs)
    print(rs)
