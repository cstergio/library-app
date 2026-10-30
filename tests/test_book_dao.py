import sqlite3
from datetime import date, timedelta

import pytest

from dao.book_dao import BookDAO
from dao.loan_dao import LoanDAO
from dao.user_dao import UserDAO
from models.book import Book
from models.loan import Loan
from models.user import User


@pytest.fixture
def dao(db_path):
    return BookDAO(db_path)


# ---------- CRUD ----------

def test_add_gives_the_book_an_id(dao):
    book = dao.add(Book("1984", "George Orwell", 1949, "978-2"))
    assert book.id is not None


def test_added_book_can_be_found_by_id(dao):
    added = dao.add(Book("1984", "George Orwell", 1949, "978-2"))

    found = dao.get_by_id(added.id)

    assert found.id == added.id
    assert found.title == "1984"
    assert found.author == "George Orwell"
    assert found.year == 1949
    assert found.isbn == "978-2"


def test_get_by_id_returns_none_when_missing(dao):
    assert dao.get_by_id(999) is None


def test_get_by_isbn(dao):
    book = dao.add(Book("1984", "George Orwell", 1949, "978-2"))
    found = dao.get_by_isbn("978-2")
    assert found.id == book.id


def test_get_by_isbn_returns_none_when_missing(dao):
    assert dao.get_by_isbn("978-9") is None


    if row is None:
        return None
    return self._row_to_book(row)


def test_book_can_be_found_by_isbn(dao):
    added = dao.add(Book("1984", "George Orwell", 1949, "978-2"))

    found = dao.get_by_isbn("978-2")

    assert found.id == added.id


def test_get_by_isbn_returns_none_when_missing(dao):
    assert dao.get_by_isbn("000") is None

def test_get_all_on_empty_database(dao):
    assert dao.get_all() == []


def test_get_all_returns_books_sorted_by_title(dao):
    dao.add(Book("Ο Μικρός Πρίγκιπας", "Antoine de Saint-Exupéry", 1943, "978-1"))
    dao.add(Book("1984", "George Orwell", 1949, "978-2"))
    dao.add(Book("Αλίκη", "Lewis Carroll", 1865, "978-3"))

    titles = [book.title for book in dao.get_all()]

    assert titles == ["1984", "Αλίκη", "Ο Μικρός Πρίγκιπας"]


def test_update_changes_the_book(dao):
    book = dao.add(Book("1984", "George Orwell", 1949, "978-2"))

    book.year = 1950
    book.title = "Νινέτι Έιτι Φορ"
    dao.update(book)

    found = dao.get_by_id(book.id)
    assert found.year == 1950
    assert found.title == "Νινέτι Έιτι Φορ"


def test_update_does_not_touch_other_books(dao):
    first = dao.add(Book("1984", "George Orwell", 1949, "978-2"))
    second = dao.add(Book("Αλίκη", "Lewis Carroll", 1865, "978-3"))

    first.year = 1950
    dao.update(first)

    assert dao.get_by_id(second.id).year == 1865


def test_delete_removes_the_book(dao):
    book = dao.add(Book("1984", "George Orwell", 1949, "978-2"))

    dao.delete(book.id)

    assert dao.get_by_id(book.id) is None
    assert dao.get_all() == []


def test_add_with_same_isbn_fails(dao):
    dao.add(Book("1984", "George Orwell", 1949, "978-2"))

    with pytest.raises(sqlite3.IntegrityError):
        dao.add(Book("Άλλο", "Κάποιος", 2000, "978-2"))


# ---------- διαθέσιμα βιβλία ----------

def lend(db_path, book):
    user = UserDAO(db_path).add(
        User(f"Χρήστης {book.id}", f"user{book.id}@example.com", "hash")
    )
    today = date(2026, 10, 1)
    return LoanDAO(db_path).add(
        Loan(book.id, user.id, today, today + timedelta(days=14))
    )


def test_all_books_are_available_when_nothing_is_loaned(dao):
    dao.add(Book("1984", "George Orwell", 1949, "978-2"))
    dao.add(Book("Αλίκη", "Lewis Carroll", 1865, "978-3"))

    titles = [book.title for book in dao.get_available()]

    assert titles == ["1984", "Αλίκη"]


def test_loaned_book_is_not_available(dao, db_path):
    loaned = dao.add(Book("1984", "George Orwell", 1949, "978-2"))
    dao.add(Book("Αλίκη", "Lewis Carroll", 1865, "978-3"))
    lend(db_path, loaned)

    titles = [book.title for book in dao.get_available()]

    assert titles == ["Αλίκη"]


def test_returned_book_is_available_again(dao, db_path):
    book = dao.add(Book("1984", "George Orwell", 1949, "978-2"))
    loan = lend(db_path, book)
    LoanDAO(db_path).mark_returned(loan.id, date(2026, 10, 5))

    titles = [book.title for book in dao.get_available()]

    assert titles == ["1984"]


def test_no_books_available_when_all_are_loaned(dao, db_path):
    book = dao.add(Book("1984", "George Orwell", 1949, "978-2"))
    lend(db_path, book)

    assert dao.get_available() == []