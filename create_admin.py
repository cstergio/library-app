"""Δημιουργεί τον πρώτο διαχειριστή της εφαρμογής."""

from getpass import getpass

from app import create_app
from models.user import User
from services.errors import ServiceError

app = create_app()

name = input("Όνομα: ")
email = input("Email: ")
password = getpass("Κωδικός (δεν φαίνεται όσο γράφετε): ")

try:
    admin = app.user_service.create(name, email, password, User.ROLE_ADMIN)
except ServiceError as error:
    print("Αποτυχία:", error)
else:
    print("Ο διαχειριστής δημιουργήθηκε:", admin)