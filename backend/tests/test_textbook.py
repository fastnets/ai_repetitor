import json

from app.textbook import TextbookSearch


def test_textbook_search_returns_relevant_chunk(tmp_path):
    path = tmp_path / "index.json"
    path.write_text(json.dumps({"chunks": [
        {"page": 1, "text": "Сложение чисел столбиком"},
        {"page": 2, "text": "Периметр прямоугольника и длины сторон"},
    ]}, ensure_ascii=False), encoding="utf-8")
    result = TextbookSearch(path).search("как найти периметр")
    assert result[0]["page"] == 2

