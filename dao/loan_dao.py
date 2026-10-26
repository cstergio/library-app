from datetime import date

from database import DB_PATH, get_connection
from models.loan import Loan


class LoanDAO:
    """Αποθήκευση και ανάγνωση δανεισμών από τη βάση."""

    SELECT_WITH_TITLE = (
        "SELECT loans.*, books.title AS book_title "
        "FROM loans "
        "JOIN books ON books.id = loans.book_id "
    )

    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path

    def add(self, loan):
        conn = get_connection(self.db_path)
        cursor = conn.execute(
            "INSERT INTO loans (book_id, user_id, loan_date, due_date) "
            "VALUES (?, ?, ?, ?)",
            (
                loan.book_id,
                loan.user_id,
                loan.loan_date.isoformat(),
                loan.due_date.isoformat(),
            ),
        )
        conn.commit()
        loan.id = cursor.lastrowid
        conn.close()
        return loan

    def get_by_id(self, loan_id):
        conn = get_connection(self.db_path)
        row = conn.execute(
            self.SELECT_WITH_TITLE + "WHERE loans.id = ?", (loan_id,)
        ).fetchone()
        conn.close()
        if row is None:
            return None
        return self._row_to_loan(row)

    def get_active_by_user(self, user_id):
        conn = get_connection(self.db_path)
        rows = conn.execute(
            self.SELECT_WITH_TITLE
            + "WHERE loans.user_id = ? AND loans.return_date IS NULL "
            + "ORDER BY loans.due_date",
            (user_id,),
        ).fetchall()
        conn.close()
        return [self._row_to_loan(row) for row in rows]

    def get_history_by_user(self, user_id):
        conn = get_connection(self.db_path)
        rows = conn.execute(
            self.SELECT_WITH_TITLE
            + "WHERE loans.user_id = ? "
            + "ORDER BY loans.loan_date DESC, loans.id DESC",
            (user_id,),
        ).fetchall()
        conn.close()
        return [self._row_to_loan(row) for row in rows]

    def count_active_by_user(self, user_id):
        conn = get_connection(self.db_path)
        row = conn.execute(
            "SELECT COUNT(*) FROM loans "
            "WHERE user_id = ? AND return_date IS NULL",
            (user_id,),
        ).fetchone()
        conn.close()
        return row[0]

    def is_book_loaned(self, book_id):
        conn = get_connection(self.db_path)
        row = conn.execute(
            "SELECT 1 FROM loans WHERE book_id = ? AND return_date IS NULL",
            (book_id,),
        ).fetchone()
        conn.close()
        return row is not None

    def mark_returned(self, loan_id, return_date):
        conn = get_connection(self.db_path)
        conn.execute(
            "UPDATE loans SET return_date = ? WHERE id = ?",
            (return_date.isoformat(), loan_id),
        )
        conn.commit()
        conn.close()

    def book_has_loans(self, book_id):
        conn = get_connection(self.db_path)
        row = conn.execute(
            "SELECT 1 FROM loans WHERE book_id = ?", (book_id,)
        ).fetchone()
        conn.close()
        return row is not None

    def user_has_loans(self, user_id):
        conn = get_connection(self.db_path)
        row = conn.execute(
            "SELECT 1 FROM loans WHERE user_id = ?", (user_id,)
        ).fetchone()
        conn.close()
        return row is not None

    def _row_to_loan(self, row):
        return_date = None
        if row["return_date"] is not None:
            return_date = date.fromisoformat(row["return_date"])

        return Loan(
            id=row["id"],
            book_id=row["book_id"],
            user_id=row["user_id"],
            loan_date=date.fromisoformat(row["loan_date"]),
            due_date=date.fromisoformat(row["due_date"]),
            return_date=return_date,
            book_title=row["book_title"],
        )