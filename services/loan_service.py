from datetime import date, timedelta

from models.loan import Loan
from services.errors import ServiceError

LOAN_DAYS = 14
MAX_ACTIVE_LOANS = 3


class LoanService:
    """Οι κανόνες για τους δανεισμούς."""

    def __init__(self, loan_dao, book_dao, today=date.today):
        self.loan_dao = loan_dao
        self.book_dao = book_dao
        self.today = today

    # ---------- δανεισμός ----------

    def borrow(self, user_id, book_id):
        book = self.book_dao.get_by_id(book_id)
        if book is None:
            raise ServiceError("Το βιβλίο δεν βρέθηκε.")

        if self.loan_dao.is_book_loaned(book.id):
            raise ServiceError("Το βιβλίο είναι ήδη δανεισμένο.")

        if self.loan_dao.count_active_by_user(user_id) >= MAX_ACTIVE_LOANS:
            raise ServiceError(
                f"Έχετε ήδη {MAX_ACTIVE_LOANS} βιβλία. "
                "Επιστρέψτε ένα για να δανειστείτε άλλο."
            )

        loan_date = self.today()
        loan = Loan(
            book_id=book.id,
            user_id=user_id,
            loan_date=loan_date,
            due_date=loan_date + timedelta(days=LOAN_DAYS),
            book_title=book.title,
        )
        return self.loan_dao.add(loan)

    # ---------- επιστροφή ----------

    def return_book(self, user_id, loan_id):
        loan = self.loan_dao.get_by_id(loan_id)

        if loan is None or loan.user_id != user_id:
            raise ServiceError("Ο δανεισμός δεν βρέθηκε.")

        if loan.is_returned():
            raise ServiceError("Το βιβλίο έχει ήδη επιστραφεί.")

        return_date = self.today()
        self.loan_dao.mark_returned(loan.id, return_date)
        loan.return_date = return_date
        return loan

    # ---------- προβολή ----------

    def active_loans(self, user_id):
        return self.loan_dao.get_active_by_user(user_id)

    def history(self, user_id):
        return self.loan_dao.get_history_by_user(user_id)