from datetime import date

from models.loan import Loan


def make_loan(return_date=None):
    return Loan(
        book_id=1,
        user_id=2,
        loan_date=date(2026, 10, 1),
        due_date=date(2026, 10, 15),
        return_date=return_date,
        book_title="1984",
    )


def test_new_loan_is_not_returned():
    loan = make_loan()
    assert loan.is_returned() is False


def test_loan_with_return_date_is_returned():
    loan = make_loan(return_date=date(2026, 10, 10))
    assert loan.is_returned() is True


def test_loan_is_not_overdue_before_due_date():
    loan = make_loan()
    assert loan.is_overdue(today=date(2026, 10, 10)) is False


def test_loan_is_not_overdue_on_due_date():
    loan = make_loan()
    assert loan.is_overdue(today=date(2026, 10, 15)) is False


def test_loan_is_overdue_after_due_date():
    loan = make_loan()
    assert loan.is_overdue(today=date(2026, 10, 16)) is True


def test_returned_loan_is_never_overdue():
    loan = make_loan(return_date=date(2026, 10, 20))
    assert loan.is_overdue(today=date(2026, 10, 25)) is False


def test_loan_as_text_with_title():
    loan = make_loan()
    assert str(loan) == "1984, έως 2026-10-15 (ενεργός)"


def test_loan_as_text_without_title():
    loan = Loan(7, 2, date(2026, 10, 1), date(2026, 10, 15))
    assert str(loan) == "βιβλίο 7, έως 2026-10-15 (ενεργός)"