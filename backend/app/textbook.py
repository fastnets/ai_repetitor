import json
import math
import re
from collections import Counter
from pathlib import Path


TOKEN_RE = re.compile(r"[а-яёa-z0-9]+", re.IGNORECASE)


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


class TextbookSearch:
    """Small replaceable local retrieval layer for the MVP."""

    def __init__(self, index_path: str | Path):
        self.index_path = Path(index_path)
        self.chunks: list[dict] = []
        self._load()

    def _load(self) -> None:
        if self.index_path.exists():
            data = json.loads(self.index_path.read_text(encoding="utf-8"))
            self.chunks = data.get("chunks", [])

    def search(self, query: str, limit: int = 3) -> list[dict]:
        if not self.chunks:
            return []
        query_terms = Counter(tokenize(query))
        if not query_terms:
            return []
        document_frequency = Counter()
        tokenized = []
        for chunk in self.chunks:
            terms = tokenize(chunk["text"])
            tokenized.append(terms)
            document_frequency.update(set(terms))
        count = len(self.chunks)
        ranked = []
        for chunk, terms in zip(self.chunks, tokenized):
            frequencies = Counter(terms)
            score = sum(
                query_terms[term] * frequencies[term] * (math.log((count + 1) / (document_frequency[term] + 1)) + 1)
                for term in query_terms
            )
            if score:
                ranked.append((score, chunk))
        ranked.sort(key=lambda item: item[0], reverse=True)
        return [chunk for _, chunk in ranked[:limit]]

