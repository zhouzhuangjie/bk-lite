from src.loader.text_loader import TextLoader


def test_load_txt_full_mode():
    loader = TextLoader(path='tests/assert/full_text_loader.txt')
    rs = loader.load()
    print(rs)
