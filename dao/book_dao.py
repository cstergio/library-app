from database import DB_PATH, get_connection
from models.book import Book


class BookDAO:
    """Αποθήκευση και ανάγνωση βιβλίων από τη βάση."""

    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path

    def add(self, book):
        conn = get_connection(self.db_path)
        cursor = conn.execute(
            "INSERT INTO books (title, author, year, isbn) VALUES (?, ?, ?, ?)",
            (book.title, book.author, book.year, book.isbn),
        )
        conn.commit()
        book.id = cursor.lastrowid
        conn.close()
        return book

    def get_by_id(self, book_id):
        conn = get_connection(self.db_path)
        row = conn.execute(
            "SELECT * FROM books WHERE id = ?", (book_id,)
        ).fetchone()
        conn.close()
        if row is None:
            return None
        return self._row_to_book(row)

    def get_all(self):
        conn = get_connection(self.db_path)
        rows = conn.execute("SELECT * FROM books ORDER BY title").fetchall()
        conn.close()
        return [self._row_to_book(row) for row in rows]

    def update(self, book):
        conn = get_connection(self.db_path)
        conn.execute(
            "UPDATE books SET title = ?, author = ?, year = ?, isbn = ? "
            "WHERE id = ?",
            (book.title, book.author, book.year, book.isbn, book.id),
        )
        conn.commit()
        conn.close()

    def delete(self, book_id):
        conn = get_connection(self.db_path)
        conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
        conn.commit()
        conn.close()

    def _row_to_book(self, row):
        return Book(
            id=row["id"],
            title=row["title"],
            author=row["author"],
            year=row["year"],
            isbn=row["isbn"],
        )