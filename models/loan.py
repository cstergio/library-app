from datetime import date


class Loan:
    """Ένας δανεισμός βιβλίου σε χρήστη."""

    def __init__(self, book_id, user_id, loan_date, due_date,
                 return_date=None, id=None, book_title=None):
        self.id = id
        self.book_id = book_id
        self.user_id = user_id
        self.loan_date = loan_date
        self.due_date = due_date
        self.return_date = return_date
        self.book_title = book_title

    def is_returned(self):
        return self.return_date is not None

    def is_overdue(self, today=None):
        if today is None:
            today = date.today()
        return not self.is_returned() and today > self.due_date

    def __str__(self):
        title = self.book_title or f"βιβλίο {self.book_id}"
        status = "επεστράφη" if self.is_returned() else "ενεργός"
        return f"{title}, έως {self.due_date} ({status})"