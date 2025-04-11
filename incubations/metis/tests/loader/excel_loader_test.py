from src.loader.excel_loader import ExcelLoader


def test_excel_loader():
    loader = ExcelLoader('tests/assert/excel_loader.xlsx', mode='full')
    print(loader.load())


def test_excel_loader_title_row_struct_load():
    loader = ExcelLoader(
        'tests/assert/excel_loader_title_chunk.xlsx', mode='full')
    print(loader.title_row_struct_load())
