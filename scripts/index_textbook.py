import argparse
import json
import re
from pathlib import Path

from pypdf import PdfReader


def split_text(text: str, size: int = 900, overlap: int = 120) -> list[str]:
    clean = re.sub(r"\s+", " ", text).strip()
    if not clean:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(clean):
        end = min(len(clean), start + size)
        if end < len(clean):
            boundary = clean.rfind(". ", start + size // 2, end)
            if boundary > start:
                end = boundary + 1
        chunks.append(clean[start:end].strip())
        if end >= len(clean):
            break
        start = max(start + 1, end - overlap)
    return chunks


def index_pdfs(pdf_paths: list[Path], output: Path) -> tuple[int, list[dict]]:
    chunks = []
    sources = []
    for source_number, pdf_path in enumerate(pdf_paths, start=1):
        reader = PdfReader(str(pdf_path))
        source_chunks = 0
        for page_number, page in enumerate(reader.pages, start=1):
            for part, text in enumerate(split_text(page.extract_text() or ""), start=1):
                chunks.append(
                    {
                        "id": f"s{source_number}-p{page_number}-{part}",
                        "source": pdf_path.name,
                        "page": page_number,
                        "text": text,
                    }
                )
                source_chunks += 1
        sources.append({"file": pdf_path.name, "pages": len(reader.pages), "chunks": source_chunks})
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps({"sources": sources, "chunks": chunks}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return len(chunks), sources


def main() -> None:
    parser = argparse.ArgumentParser(description="Создать локальный индекс учебника PDF")
    parser.add_argument("pdf", type=Path, nargs="+")
    parser.add_argument("--output", type=Path, default=Path("data/textbooks/index.json"))
    args = parser.parse_args()
    missing = [path for path in args.pdf if not path.is_file()]
    if missing:
        parser.error(f"Файл не найден: {missing[0]}")
    count, sources = index_pdfs(args.pdf, args.output)
    for source in sources:
        print(f"{source['file']}: {source['pages']} стр., {source['chunks']} фрагментов")
    print(f"Готово: всего {count} фрагментов сохранено в {args.output}")


if __name__ == "__main__":
    main()
