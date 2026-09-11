import argparse
import sqlite3
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Найти занятие по тексту сообщения")
    parser.add_argument("query")
    parser.add_argument("--db", type=Path, required=True)
    args = parser.parse_args()
    with sqlite3.connect(args.db) as db:
        rows = db.execute(
            """
            SELECT session_id, content
            FROM messages
            WHERE lower(content) LIKE lower(?)
            ORDER BY id DESC
            LIMIT 10
            """,
            (f"%{args.query}%",),
        ).fetchall()
    for session_id, content in rows:
        print(f"{session_id}\t{content[:160].replace(chr(10), ' ')}")


if __name__ == "__main__":
    main()
