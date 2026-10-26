from datetime import date, timedelta

import pytest

from dao.book_dao import BookDAO
from dao.loan_dao import LoanDAO
from dao.user_dao import UserDAO
from models.book import Book
from models.loan import Loan
from models.user import User


@pytest.fixture
def loan_dao(db_path):
    return LoanDAO(db_path)


@pytest.fixture
def book(db_path):
    return BookDAO(db_path).add(Book("1984", "George Orwell", 1949, "978-2"))


@pytest.fixture
def other_book(db_path):
    return BookDAO(db_path).add(Book("Αλίκη", "Lewis Carroll", 1865, "978-3"))


@pytest.fixture
def user(db_path):
    return UserDAO(db_path).add(User("Μαρία", "maria@example.com", "hash"))


@pytest.fixture
def other_user(db_path):
    return UserDAO(db_path).add(User("Νίκος", "nikos@example.com", "hash"))


def make_loan(book, user, loan_date=date(2026, 10, 1), days=14):
    return Loan(
        book_id=book.id,
        user_id=user.id,
        loan_date=loan_date,
        due_date=loan_date + timedelta(days=days),
    )


# ---------- add και get_by_id ----------

def test_add_gives_the_loan_an_id(loan_dao, book, user):
    loan = loan_dao.add(make_loan(book, user))
    assert loan.id is not None


def test_added_loan_can_be_found_with_dates_and_title(loan_dao, book, user):
    added = loan_dao.add(make_loan(book, user))

    found = loan_dao.get_by_id(added.id)

    assert found.book_id == book.id
    assert found.user_id == user.id
    assert found.loan_date == date(2026, 10, 1)
    assert found.due_date == date(2026, 10, 15)
    assert found.return_date is None
    assert found.book_title == "1984"


def test_get_by_id_returns_none_when_missing(loan_dao):
    assert loan_dao.get_by_id(999) is None


# ---------- mark_returned ----------

def test_mark_returned_saves_the_return_date(loan_dao, book, user):
    loan = loan_dao.add(make_loan(book, user))

    loan_dao.mark_returned(loan.id, date(2026, 10, 10))

    found = loan_dao.get_by_id(loan.id)
    assert found.return_date == date(2026, 10, 10)
    assert found.is_returned() is True


# ---------- ενεργοί δανεισμοί ----------

def test_active_loans_exclude_returned_ones(loan_dao, book, other_book, user):
    returned = loan_dao.add(make_loan(book, user))
    loan_dao.add(make_loan(other_book, user))
    loan_dao.mark_returned(returned.id, date(2026, 10, 5))

    active = loan_dao.get_active_by_user(user.id)

    assert [loan.book_title for loan in active] == ["Αλίκη"]


def test_active_loans_are_sorted_by_due_date(loan_dao, book, other_book, user):
    loan_dao.add(make_loan(book, user, days=20))
    loan_dao.add(make_loan(other_book, user, days=5))

    active = loan_dao.get_active_by_user(user.id)

    assert [loan.book_title for loan in active] == ["Αλίκη", "1984"]


def test_active_loans_belong_only_to_that_user(loan_dao, book, other_book,
                                               user, other_user):
    loan_dao.add(make_loan(book, user))
    loan_dao.add(make_loan(other_book, other_user))

    active = loan_dao.get_active_by_user(user.id)

    assert [loan.book_title for loan in active] == ["1984"]


# ---------- ιστορικό ----------

def test_history_includes_returned_loans_newest_first(loan_dao, book,
                                                      other_book, user):
    old = loan_dao.add(make_loan(book, user, loan_date=date(2026, 10, 1)))
    loan_dao.mark_returned(old.id, date(2026, 10, 3))
    loan_dao.add(make_loan(other_book, user, loan_date=date(2026, 10, 5)))

    history = loan_dao.get_history_by_user(user.id)

    assert [loan.book_title for loan in history] == ["Αλίκη", "1984"]
    assert history[0].is_returned() is False
    assert history[1].is_returned() is True


def test_history_is_empty_for_new_user(loan_dao, user):
    assert loan_dao.get_history_by_user(user.id) == []


# ---------- μέτρημα ----------

def test_count_active_counts_only_active_loans(loan_dao, book, other_book, user):
    first = loan_dao.add(make_loan(book, user))
    loan_dao.add(make_loan(other_book, user))
    assert loan_dao.count_active_by_user(user.id) == 2

    loan_dao.mark_returned(first.id, date(2026, 10, 5))
    assert loan_dao.count_active_by_user(user.id) == 1


# ---------- είναι δανεισμένο; ----------

def test_book_is_not_loaned_at_start(loan_dao, book):
    assert loan_dao.is_book_loaned(book.id) is False


def test_book_is_loaned_after_add(loan_dao, book, user):
    loan_dao.add(make_loan(book, user))
    assert loan_dao.is_book_loaned(book.id) is True


def test_book_is_available_again_after_return(loan_dao, book, user):
    loan = loan_dao.add(make_loan(book, user))
    loan_dao.mark_returned(loan.id, date(2026, 10, 5))
    assert loan_dao.is_book_loaned(book.id) is False


# ---------- έχει ιστορικό; ----------

def test_book_and_user_without_loans(loan_dao, book, user):
    assert loan_dao.book_has_loans(book.id) is False
    assert loan_dao.user_has_loans(user.id) is False


def test_book_and_user_keep_history_after_return(loan_dao, book, user):
    loan = loan_dao.add(make_loan(book, user))
    loan_dao.mark_returned(loan.id, date(2026, 10, 5))

    assert loan_dao.book_has_loans(book.id) is True
    assert loan_dao.user_has_loans(user.id) is True