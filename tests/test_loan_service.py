from datetime import date, timedelta

import pytest

from dao.book_dao import BookDAO
from dao.loan_dao import LoanDAO
from dao.user_dao import UserDAO
from models.book import Book
from models.user import User
from services.errors import ServiceError
from services.loan_service import LoanService

TODAY = date(2026, 10, 1)


# ---------- fixtures ----------

@pytest.fixture
def book_dao(db_path):
    return BookDAO(db_path)


@pytest.fixture
def loan_dao(db_path):
    return LoanDAO(db_path)


@pytest.fixture
def service(loan_dao, book_dao):
    return LoanService(loan_dao, book_dao, today=lambda: TODAY)


@pytest.fixture
def maria(db_path):
    return UserDAO(db_path).add(User("Μαρία", "maria@example.com", "hash"))


@pytest.fixture
def nikos(db_path):
    return UserDAO(db_path).add(User("Νίκος", "nikos@example.com", "hash"))


def add_book(book_dao, title, isbn):
    return book_dao.add(Book(title, "Συγγραφέας", 2000, isbn))


# ---------- δανεισμός ----------

def test_borrow_creates_loan_for_14_days(service, book_dao, maria):
    book = add_book(book_dao, "1984", "978-2")

    loan = service.borrow(maria.id, book.id)

    assert loan.id is not None
    assert loan.loan_date == TODAY
    assert loan.due_date == date(2026, 10, 15)


def test_borrow_keeps_the_book_title(service, book_dao, maria):
    book = add_book(book_dao, "1984", "978-2")

    loan = service.borrow(maria.id, book.id)

    assert loan.book_title == "1984"


def test_borrowed_book_is_no_longer_available(service, book_dao, maria):
    book = add_book(book_dao, "1984", "978-2")

    service.borrow(maria.id, book.id)

    assert book_dao.get_available() == []


def test_cannot_borrow_missing_book(service, maria):
    with pytest.raises(ServiceError, match="δεν βρέθηκε"):
        service.borrow(maria.id, 999)


def test_cannot_borrow_book_that_is_already_loaned(service, book_dao,
                                                    maria, nikos):
    book = add_book(book_dao, "1984", "978-2")
    service.borrow(nikos.id, book.id)

    with pytest.raises(ServiceError, match="ήδη δανεισμένο"):
        service.borrow(maria.id, book.id)


def test_user_can_borrow_up_to_three_books(service, book_dao, maria):
    for number in range(3):
        book = add_book(book_dao, f"Βιβλίο {number}", f"isbn-{number}")
        service.borrow(maria.id, book.id)

    assert len(service.active_loans(maria.id)) == 3


def test_user_cannot_borrow_a_fourth_book(service, book_dao, maria):
    for number in range(3):
        book = add_book(book_dao, f"Βιβλίο {number}", f"isbn-{number}")
        service.borrow(maria.id, book.id)
    fourth = add_book(book_dao, "Τέταρτο", "isbn-4")

    with pytest.raises(ServiceError, match="3 βιβλία"):
        service.borrow(maria.id, fourth.id)


def test_after_returning_one_user_can_borrow_again(service, book_dao, maria):
    loans = []
    for number in range(3):
        book = add_book(book_dao, f"Βιβλίο {number}", f"isbn-{number}")
        loans.append(service.borrow(maria.id, book.id))
    fourth = add_book(book_dao, "Τέταρτο", "isbn-4")

    service.return_book(maria.id, loans[0].id)
    loan = service.borrow(maria.id, fourth.id)

    assert loan.book_title == "Τέταρτο"


# ---------- επιστροφή ----------

def test_return_saves_the_day_of_return(loan_dao, book_dao, maria):
    book = add_book(book_dao, "1984", "978-2")
    day_one = LoanService(loan_dao, book_dao, today=lambda: TODAY)
    day_ten = LoanService(loan_dao, book_dao,
                          today=lambda: TODAY + timedelta(days=9))

    loan = day_one.borrow(maria.id, book.id)
    day_ten.return_book(maria.id, loan.id)

    assert loan_dao.get_by_id(loan.id).return_date == date(2026, 10, 10)


def test_returned_book_is_available_again(service, book_dao, maria):
    book = add_book(book_dao, "1984", "978-2")
    loan = service.borrow(maria.id, book.id)

    service.return_book(maria.id, loan.id)

    assert [b.title for b in book_dao.get_available()] == ["1984"]


def test_user_cannot_return_someone_elses_loan(service, book_dao,
                                                maria, nikos):
    book = add_book(book_dao, "1984", "978-2")
    loan = service.borrow(nikos.id, book.id)

    with pytest.raises(ServiceError, match="δεν βρέθηκε"):
        service.return_book(maria.id, loan.id)

    assert service.active_loans(nikos.id)[0].id == loan.id


def test_cannot_return_missing_loan(service, maria):
    with pytest.raises(ServiceError, match="δεν βρέθηκε"):
        service.return_book(maria.id, 999)


def test_cannot_return_the_same_book_twice(service, book_dao, maria):
    book = add_book(book_dao, "1984", "978-2")
    loan = service.borrow(maria.id, book.id)
    service.return_book(maria.id, loan.id)

    with pytest.raises(ServiceError, match="ήδη επιστραφεί"):
        service.return_book(maria.id, loan.id)


# ---------- προβολή ----------

def test_active_loans_show_only_not_returned(service, book_dao, maria):
    first = add_book(book_dao, "1984", "978-2")
    second = add_book(book_dao, "Αλίκη", "978-3")
    loan = service.borrow(maria.id, first.id)
    service.borrow(maria.id, second.id)

    service.return_book(maria.id, loan.id)

    assert [l.book_title for l in service.active_loans(maria.id)] == ["Αλίκη"]


def test_history_keeps_returned_loans(service, book_dao, maria):
    book = add_book(book_dao, "1984", "978-2")
    loan = service.borrow(maria.id, book.id)
    service.return_book(maria.id, loan.id)

    history = service.history(maria.id)

    assert len(history) == 1
    assert history[0].is_returned() is True


def test_loan_becomes_overdue_after_14_days(service, book_dao, maria):
    book = add_book(book_dao, "1984", "978-2")
    loan = service.borrow(maria.id, book.id)

    assert loan.is_overdue(today=TODAY + timedelta(days=14)) is False
    assert loan.is_overdue(today=TODAY + timedelta(days=15)) is True