import sqlite3

import pytest

from dao.book_dao import BookDAO
from models.book import Book


@pytest.fixture
def dao(db_path):
    return BookDAO(db_path)


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