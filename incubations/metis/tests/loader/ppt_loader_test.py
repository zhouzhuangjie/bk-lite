from src.loader.ppt_loader import PPTLoader


def test_ppt_loader():
    loader = PPTLoader('../assert/ppt_loader.pptx')
    rs = loader.load()
    print(rs)
