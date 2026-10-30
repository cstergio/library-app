from datetime import date, timedelta

import pytest

from dao.book_dao import BookDAO
from dao.loan_dao import LoanDAO
from dao.user_dao import UserDAO
from models.loan import Loan
from models.user import User
from services.book_service import BookService
from services.errors import ServiceError


@pytest.fixture
def service(db_path):
    return BookService(BookDAO(db_path), LoanDAO(db_path))


def lend(db_path, book):
    user = UserDAO(db_path).add(User("Μαρία", "maria@example.com", "hash"))
    today = date(2026, 10, 1)
    return LoanDAO(db_path).add(
        Loan(book.id, user.id, today, today + timedelta(days=14))
    )


# ---------- δημιουργία ----------

def test_create_saves_the_book(service):
    book = service.create("1984", "George Orwell", "1949", "978-2")

    assert book.id is not None
    assert service.get(book.id).title == "1984"


def test_create_removes_extra_spaces(service):
    book = service.create("  1984 ", " George Orwell  ", " 1949 ", " 978-2 ")

    assert book.title == "1984"
    assert book.author == "George Orwell"
    assert book.year == 1949
    assert book.isbn == "978-2"


def test_create_requires_title(service):
    with pytest.raises(ServiceError, match="τίτλος"):
        service.create("", "George Orwell", "1949", "978-2")


def test_title_with_only_spaces_is_empty(service):
    with pytest.raises(ServiceError, match="τίτλος"):
        service.create("    ", "George Orwell", "1949", "978-2")


def test_create_requires_author(service):
    with pytest.raises(ServiceError, match="συγγραφέας"):
        service.create("1984", "", "1949", "978-2")


# ---------- έτος ----------

def test_year_text_becomes_number(service):
    book = service.create("1984", "George Orwell", "1949", None)
    assert book.year == 1949


def test_empty_year_is_allowed(service):
    book = service.create("1984", "George Orwell", "", None)
    assert book.year is None


def test_year_must_be_a_number(service):
    with pytest.raises(ServiceError, match="αριθμός"):
        service.create("1984", "George Orwell", "χίλια", None)


def test_year_cannot_be_in_the_future(service):
    next_year = str(date.today().year + 1)

    with pytest.raises(ServiceError, match="έγκυρο"):
        service.create("1984", "George Orwell", next_year, None)


def test_year_cannot_be_negative(service):
    with pytest.raises(ServiceError, match="έγκυρο"):
        service.create("1984", "George Orwell", "-5", None)


# ---------- ISBN ----------

def test_empty_isbn_becomes_none(service):
    book = service.create("1984", "George Orwell", "1949", "   ")
    assert book.isbn is None


def test_many_books_without_isbn_are_allowed(service):
    service.create("1984", "George Orwell", "1949", "")
    service.create("Αλίκη", "Lewis Carroll", "1865", "")

    assert len(service.list_all()) == 2


def test_create_rejects_duplicate_isbn(service):
    service.create("1984", "George Orwell", "1949", "978-2")

    with pytest.raises(ServiceError, match="ISBN"):
        service.create("Άλλο", "Κάποιος", "2000", "978-2")


# ---------- εύρεση ----------

def test_get_missing_book_fails(service):
    with pytest.raises(ServiceError, match="δεν βρέθηκε"):
        service.get(999)


# ---------- αλλαγή ----------

def test_update_changes_the_book(service):
    book = service.create("1984", "George Orwell", "1949", "978-2")

    service.update(book.id, "Νέος τίτλος", "George Orwell", "1950", "978-2")

    found = service.get(book.id)
    assert found.title == "Νέος τίτλος"
    assert found.year == 1950


def test_update_can_keep_the_same_isbn(service):
    book = service.create("1984", "George Orwell", "1949", "978-2")

    service.update(book.id, "Νέος τίτλος", "George Orwell", "1949", "978-2")

    assert service.get(book.id).isbn == "978-2"


def test_update_rejects_isbn_of_another_book(service):
    service.create("1984", "George Orwell", "1949", "978-2")
    other = service.create("Αλίκη", "Lewis Carroll", "1865", "978-3")

    with pytest.raises(ServiceError, match="ISBN"):
        service.update(other.id, "Αλίκη", "Lewis Carroll", "1865", "978-2")


def test_update_also_checks_the_rules(service):
    book = service.create("1984", "George Orwell", "1949", "978-2")

    with pytest.raises(ServiceError, match="τίτλος"):
        service.update(book.id, "", "George Orwell", "1949", "978-2")


def test_update_missing_book_fails(service):
    with pytest.raises(ServiceError, match="δεν βρέθηκε"):
        service.update(999, "1984", "George Orwell", "1949", None)


# ---------- διαγραφή ----------

def test_delete_removes_the_book(service):
    book = service.create("1984", "George Orwell", "1949", "978-2")

    service.delete(book.id)

    assert service.list_all() == []


def test_cannot_delete_book_with_loans(service, db_path):
    book = service.create("1984", "George Orwell", "1949", "978-2")
    lend(db_path, book)

    with pytest.raises(ServiceError, match="δανεισμούς"):
        service.delete(book.id)

    assert service.get(book.id).title == "1984"


def test_delete_missing_book_fails(service):
    with pytest.raises(ServiceError, match="δεν βρέθηκε"):
        service.delete(999)


# ---------- διαθέσιμα ----------

def test_list_available_hides_loaned_books(service, db_path):
    loaned = service.create("1984", "George Orwell", "1949", "978-2")
    service.create("Αλίκη", "Lewis Carroll", "1865", "978-3")
    lend(db_path, loaned)

    titles = [book.title for book in service.list_available()]

    assert titles == ["Αλίκη"]