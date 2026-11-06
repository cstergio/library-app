"""Προσθέτει μερικά βιβλία στη βάση, για δοκιμές."""

from app import create_app
from services.errors import ServiceError

BOOKS = [
    ("Ο Μικρός Πρίγκιπας", "Antoine de Saint-Exupéry", "1943", "978-1"),
    ("1984", "George Orwell", "1949", "978-2"),
    ("Η Αλίκη στη Χώρα των Θαυμάτων", "Lewis Carroll", "1865", "978-3"),
    ("Ο Άρχοντας των Δαχτυλιδιών", "J.R.R. Tolkien", "1954", "978-4"),
    ("Ζορμπάς", "Νίκος Καζαντζάκης", "1946", "978-5"),
]

app = create_app()

for title, author, year, isbn in BOOKS:
    try:
        app.book_service.create(title, author, year, isbn)
        print("Προστέθηκε", title)
    except ServiceError as error:
        print("Παραλείφθηκε", title, "-", error)