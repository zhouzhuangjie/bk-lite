from src.loader.doc_loader import DocLoader


def test_load_docs():
    loader = DocLoader('../assert/pdf_word_raw.docx')
    print(loader.load())
