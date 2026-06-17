import os
from contextlib import contextmanager
from decimal import Decimal

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/biblioteca_universitaria",
)


@contextmanager
def get_cursor():
    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
        try:
            with conn.cursor() as cur:
                yield conn, cur
            conn.commit()
        except Exception:
            conn.rollback()
            raise


def rows_to_list(rows):
    result = []
    for row in rows:
        item = dict(row)
        for key, val in item.items():
            if hasattr(val, "isoformat"):
                item[key] = val.isoformat()
            elif isinstance(val, Decimal):
                item[key] = float(val)
        result.append(item)
    return result


def row_to_dict(row):
    if row is None:
        return None
    return rows_to_list([row])[0]
