import requests


def test_ingest():
    rs = requests.post('http://localhost:18083/api/rag/ingest',
                       files={'file': open('../assert/full_text_loader.txt', 'rb')},
                       data={'index_name': 'test_index'})
    print(rs.json())
