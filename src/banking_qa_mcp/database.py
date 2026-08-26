from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any

DEFAULT_DB = Path(__file__).resolve().parents[2] / "data" / "banking_qa.db"


def db_path() -> Path:
    return Path(os.getenv("BANKING_QA_DB", DEFAULT_DB))


def connect() -> sqlite3.Connection:
    connection = sqlite3.connect(db_path())
    connection.row_factory = sqlite3.Row
    return connection


def rows(query: str, parameters: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    with connect() as connection:
        return [dict(row) for row in connection.execute(query, parameters).fetchall()]


def row(query: str, parameters: tuple[Any, ...] = ()) -> dict[str, Any] | None:
    result = rows(query, parameters)
    return result[0] if result else None
