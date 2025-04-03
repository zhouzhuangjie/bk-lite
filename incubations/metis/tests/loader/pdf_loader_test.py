from src.loader.pdf_loader import PDFLoader


def test_load_pdf():
    loader = PDFLoader(file_path="../assert/pdf_word_raw.pdf")
    print(loader.load())
