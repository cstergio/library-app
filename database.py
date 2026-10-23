import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "library.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"


def get_connection():
    """Ανοίγει σύνδεση με τη βάση."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Δημιουργεί τους πίνακες, αν δεν υπάρχουν."""
    conn = get_connection()
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.close()