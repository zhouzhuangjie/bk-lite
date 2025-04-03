from src.loader.excel_loader import ExcelLoader


def test_excel_loader():
    loader = ExcelLoader('../assert/excel_loader.xlsx')
    print(loader.load())
