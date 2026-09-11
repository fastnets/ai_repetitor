import argparse
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.textbook import TextbookSearch


def main() -> None:
    parser = argparse.ArgumentParser(description="Проверить поиск по индексу учебника")
    parser.add_argument("query")
    parser.add_argument("--index", type=Path, default=ROOT / "data/textbooks/index.json")
    args = parser.parse_args()
    results = TextbookSearch(args.index).search(args.query)
    if not results:
        print("Ничего не найдено")
        return
    for item in results:
        preview = item["text"][:300].replace("\n", " ")
        print(f"{item.get('source', 'учебник')}, стр. {item.get('page', '?')}: {preview}")


if __name__ == "__main__":
    main()
