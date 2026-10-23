from datetime import date


class Loan:
    """Ένας δανεισμός βιβλίου σε μέλος."""

    def __init__(self, book_id, member_id, loan_date, due_date,
                 return_date=None, id=None):
        self.id = id
        self.book_id = book_id
        self.member_id = member_id
        self.loan_date = loan_date
        self.due_date = due_date
        self.return_date = return_date

    def is_returned(self):
        return self.return_date is not None

    def is_overdue(self, today=None):
        if today is None:
            today = date.today()
        return not self.is_returned() and today > self.due_date

    def __str__(self):
        status = "επεστράφη" if self.is_returned() else "ενεργός"
        return f"Δανεισμός βιβλίου {self.book_id} σε μέλος {self.member_id} ({status})"