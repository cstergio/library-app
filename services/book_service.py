from datetime import date

from models.book import Book
from services.errors import ServiceError


class BookService:
    """Οι κανόνες της βιβλιοθήκης για τα βιβλία."""

    def __init__(self, book_dao, loan_dao):
        self.book_dao = book_dao
        self.loan_dao = loan_dao

    # ---------- ανάγνωση ----------

    def list_all(self):
        return self.book_dao.get_all()

    def list_available(self):
        return self.book_dao.get_available()

    def get(self, book_id):
        book = self.book_dao.get_by_id(book_id)
        if book is None:
            raise ServiceError("Το βιβλίο δεν βρέθηκε.")
        return book

    # ---------- αλλαγές ----------

    def create(self, title, author, year, isbn):
        title, author, year, isbn = self._clean(title, author, year, isbn)

        if isbn is not None and self.book_dao.get_by_isbn(isbn) is not None:
            raise ServiceError("Υπάρχει ήδη βιβλίο με αυτό το ISBN.")

        return self.book_dao.add(Book(title, author, year, isbn))

    def update(self, book_id, title, author, year, isbn):
        book = self.get(book_id)
        title, author, year, isbn = self._clean(title, author, year, isbn)

        if isbn is not None:
            other = self.book_dao.get_by_isbn(isbn)
            if other is not None and other.id != book.id:
                raise ServiceError("Υπάρχει ήδη άλλο βιβλίο με αυτό το ISBN.")

        book.title = title
        book.author = author
        book.year = year
        book.isbn = isbn
        self.book_dao.update(book)
        return book

    def delete(self, book_id):
        book = self.get(book_id)

        if self.loan_dao.book_has_loans(book.id):
            raise ServiceError(
                "Το βιβλίο έχει δανεισμούς και δεν μπορεί να διαγραφεί."
            )

        self.book_dao.delete(book.id)

    # ---------- έλεγχος στοιχείων ----------

    def _clean(self, title, author, year, isbn):
        title = (title or "").strip()
        author = (author or "").strip()
        isbn = (isbn or "").strip() or None

        if not title:
            raise ServiceError("Ο τίτλος είναι υποχρεωτικός.")
        if not author:
            raise ServiceError("Ο συγγραφέας είναι υποχρεωτικός.")

        year = self._parse_year(year)
        return title, author, year, isbn

    def _parse_year(self, year):
        if year is None or str(year).strip() == "":
            return None

        try:
            year = int(year)
        except ValueError:
            raise ServiceError("Το έτος πρέπει να είναι αριθμός.")

        if year < 0 or year > date.today().year:
            raise ServiceError("Το έτος δεν είναι έγκυρο.")

        return year