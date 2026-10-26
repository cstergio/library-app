from models.book import Book


def test_new_book_has_no_id():
    book = Book("1984", "George Orwell", 1949, "978-2")
    assert book.id is None


def test_book_keeps_its_data():
    book = Book("1984", "George Orwell", 1949, "978-2")
    assert book.title == "1984"
    assert book.author == "George Orwell"
    assert book.year == 1949
    assert book.isbn == "978-2"


def test_book_with_id():
    book = Book("1984", "George Orwell", 1949, "978-2", id=5)
    assert book.id == 5


def test_book_as_text():
    book = Book("1984", "George Orwell", 1949, "978-2")
    assert str(book) == "1984 (George Orwell, 1949)"