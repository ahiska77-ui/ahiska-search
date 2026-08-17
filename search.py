import csv
import json
import os
import sqlite3


DATA_DIR = "uploads"


def normalize(value):
    return str(value).strip().lower()


def search_file(path, query):
    query = normalize(query)
    results = []

    ext = os.path.splitext(path)[1].lower()

    try:
        if ext == ".txt":
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if query in normalize(line):
                        results.append(line.strip())

        elif ext == ".csv":
            with open(
                path,
                "r",
                encoding="utf-8",
                errors="ignore",
                newline=""
            ) as f:

                reader = csv.DictReader(f)

                for row in reader:
                    if any(
                        query in normalize(v)
                        for v in row.values()
                        if v is not None
                    ):
                        results.append(dict(row))

        elif ext == ".json":
            with open(
                path,
                "r",
                encoding="utf-8",
                errors="ignore"
            ) as f:

                data = json.load(f)

            def walk(obj):
                if isinstance(obj, dict):
                    if any(
                        query in normalize(v)
                        for v in obj.values()
                        if isinstance(v, (str, int, float))
                    ):
                        results.append(obj)

                    for value in obj.values():
                        walk(value)

                elif isinstance(obj, list):
                    for item in obj:
                        walk(item)

            walk(data)

        elif ext in (".db", ".sqlite", ".sqlite3"):
            con = sqlite3.connect(path)
            cur = con.cursor()

            tables = cur.execute("""
                SELECT name
                FROM sqlite_master
                WHERE type='table'
            """).fetchall()

            for (table,) in tables:
                try:
                    rows = cur.execute(
                        f'SELECT * FROM "{table}"'
                    ).fetchall()

                    columns = [
                        x[1]
                        for x in cur.execute(
                            f'PRAGMA table_info("{table}")'
                        ).fetchall()
                    ]

                    for row in rows:
                        if any(
                            query in normalize(value)
                            for value in row
                        ):
                            results.append(
                                dict(zip(columns, row))
                            )

                except Exception:
                    continue

            con.close()

    except Exception:
        pass

    return results


def search_all(query):
    os.makedirs(DATA_DIR, exist_ok=True)

    results = []

    for filename in os.listdir(DATA_DIR):
        path = os.path.join(DATA_DIR, filename)

        if os.path.isfile(path):
            results.extend(
                search_file(path, query)
            )

    return results
