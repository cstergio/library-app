import sqlite3

import pytest

from database import get_connection, init_db


@pytest.fixture
def db_path(tmp_path):
    path = tmp_path / "test.db"
    init_db(path)
    return path


def test_init_db_creates_all_tables(db_path):
    conn = get_connection(db_path)
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'"
    ).fetchall()
    conn.close()

    table_names = {row["name"] for row in rows}
    assert "books" in table_names
    assert "users" in table_names
    assert "loans" in table_names


def test_init_db_can_run_twice(db_path):
    init_db(db_path)


def test_book_isbn_must_be_unique(db_path):
    conn = get_connection(db_path)
    sql = "INSERT INTO books (title, author, year, isbn) VALUES (?, ?, ?, ?)"
    conn.execute(sql, ("1984", "George Orwell", 1949, "978-2"))

    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(sql, ("Άλλο βιβλίο", "Κάποιος", 2000, "978-2"))

    conn.close()


def test_user_role_defaults_to_user(db_path):
    conn = get_connection(db_path)
    conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Μαρία", "maria@example.com", "hash"),
    )
    row = conn.execute("SELECT role FROM users").fetchone()
    conn.close()

    assert row["role"] == "user"


def test_user_role_must_be_valid(db_path):
    conn = get_connection(db_path)

    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO users (name, email, password_hash, role) "
            "VALUES (?, ?, ?, ?)",
            ("Μαρία", "maria@example.com", "hash", "superhero"),
        )

    conn.close()


def test_loan_needs_existing_book_and_user(db_path):
    conn = get_connection(db_path)

    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO loans (book_id, user_id, loan_date, due_date) "
            "VALUES (?, ?, ?, ?)",
            (999, 999, "2026-10-26", "2026-11-09"),
        )

    conn.close()