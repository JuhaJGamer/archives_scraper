import json
from archives_scraper import parse_na, parse_categories, parse_legal_text

def test_na():
    data_in = ""
    data_out = []
    with open('tests/na_test_data.txt') as f:
        data_in = f.read()
    with open('tests/na_test_data.json') as f:
        data_out = f.read()
    # print(json.dumps(parse_na(data_in)))
    assert parse_na(data_in) == json.loads(data_out)

def test_categories():
    data_in = ""
    data_out = []
    with open('tests/na_test_data.txt') as f:
        data_in = f.read()
    with open('tests/cat_test_data.json') as f:
        data_out = f.read()
    assert json.loads(json.dumps(parse_categories(parse_na(data_in)))) == json.loads(data_out)

def test_legal_text():
    data_in = ""
    data_out = []
    with open('tests/lt_test_data.txt') as f:
        data_in = f.read()
    with open('tests/lt_test_data.json') as f:
        data_out = f.read()
    assert json.loads(json.dumps(parse_legal_text(data_in))) == json.loads(data_out)



