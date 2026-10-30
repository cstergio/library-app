from datetime import date, timedelta

import pytest

from dao.book_dao import BookDAO
from dao.loan_dao import LoanDAO
from dao.user_dao import UserDAO
from models.book import Book
from models.loan import Loan
from models.user import User
from services.errors import ServiceError
from services.user_service import UserService


@pytest.fixture
def service(db_path):
    return UserService(UserDAO(db_path), LoanDAO(db_path))


@pytest.fixture
def maria(service):
    return service.register("Μαρία", "maria@example.com", "123456")


# ---------- εγγραφή ----------

def test_register_creates_a_simple_user(service):
    user = service.register("Μαρία", "maria@example.com", "123456")

    assert user.id is not None
    assert user.role == User.ROLE_USER
    assert user.is_admin() is False


def test_password_is_never_stored_as_is(maria):
    assert maria.password_hash != "123456"
    assert "123456" not in maria.password_hash


def test_email_is_cleaned_and_lowercased(service):
    user = service.register("Μαρία", "  Maria@Example.COM ", "123456")
    assert user.email == "maria@example.com"


def test_register_requires_name(service):
    with pytest.raises(ServiceError, match="όνομα"):
        service.register("   ", "maria@example.com", "123456")


def test_register_requires_email(service):
    with pytest.raises(ServiceError, match="υποχρεωτικό"):
        service.register("Μαρία", "", "123456")


@pytest.mark.parametrize("bad_email", ["maria", "@example.com", "maria@"])
def test_register_rejects_invalid_email(service, bad_email):
    with pytest.raises(ServiceError, match="έγκυρο"):
        service.register("Μαρία", bad_email, "123456")


def test_register_rejects_short_password(service):
    with pytest.raises(ServiceError, match="κωδικός"):
        service.register("Μαρία", "maria@example.com", "12345")


def test_register_rejects_used_email_in_any_case(service, maria):
    with pytest.raises(ServiceError, match="χρησιμοποιείται"):
        service.register("Άλλη", "MARIA@example.com", "abcdef")


# ---------- σύνδεση ----------

def test_authenticate_with_correct_details(service, maria):
    user = service.authenticate("maria@example.com", "123456")
    assert user.id == maria.id


def test_authenticate_ignores_email_case(service, maria):
    user = service.authenticate("  MARIA@example.com ", "123456")
    assert user.id == maria.id


def test_authenticate_with_wrong_password_fails(service, maria):
    with pytest.raises(ServiceError, match="Λάθος"):
        service.authenticate("maria@example.com", "λάθος")


def test_unknown_email_gives_the_same_message(service, maria):
    with pytest.raises(ServiceError) as wrong_password:
        service.authenticate("maria@example.com", "λάθος")

    with pytest.raises(ServiceError) as unknown_email:
        service.authenticate("kanenas@example.com", "123456")

    assert str(wrong_password.value) == str(unknown_email.value)


# ---------- δημιουργία από admin ----------

def test_admin_can_create_another_admin(service):
    user = service.create("Νίκος", "nikos@example.com", "123456",
                          User.ROLE_ADMIN)
    assert user.is_admin() is True


def test_create_rejects_unknown_role(service):
    with pytest.raises(ServiceError, match="ρόλος"):
        service.create("Νίκος", "nikos@example.com", "123456", "superhero")


# ---------- εύρεση ----------

def test_get_missing_user_fails(service):
    with pytest.raises(ServiceError, match="δεν βρέθηκε"):
        service.get(999)


# ---------- αλλαγή ----------

def test_update_changes_name_and_role(service, maria):
    service.update(maria.id, "Μαρία Π.", "maria@example.com", User.ROLE_ADMIN)

    found = service.get(maria.id)
    assert found.name == "Μαρία Π."
    assert found.is_admin() is True


def test_update_can_keep_the_same_email(service, maria):
    service.update(maria.id, "Μαρία Π.", "maria@example.com", User.ROLE_USER)
    assert service.get(maria.id).email == "maria@example.com"


def test_update_rejects_email_of_another_user(service, maria):
    nikos = service.register("Νίκος", "nikos@example.com", "123456")

    with pytest.raises(ServiceError, match="χρησιμοποιείται"):
        service.update(nikos.id, "Νίκος", "maria@example.com", User.ROLE_USER)


def test_update_without_password_keeps_the_old_one(service, maria):
    service.update(maria.id, "Μαρία Π.", "maria@example.com", User.ROLE_USER)

    assert service.authenticate("maria@example.com", "123456").id == maria.id


def test_update_with_new_password_changes_it(service, maria):
    service.update(maria.id, "Μαρία", "maria@example.com", User.ROLE_USER,
                   new_password="νέος-κωδικός")

    assert service.authenticate("maria@example.com", "νέος-κωδικός").id == maria.id
    with pytest.raises(ServiceError):
        service.authenticate("maria@example.com", "123456")


def test_update_rejects_short_new_password(service, maria):
    with pytest.raises(ServiceError, match="κωδικός"):
        service.update(maria.id, "Μαρία", "maria@example.com", User.ROLE_USER,
                       new_password="123")


# ---------- διαγραφή ----------

def test_admin_can_delete_another_user(service, maria):
    admin = service.create("Admin", "admin@library.gr", "123456",
                           User.ROLE_ADMIN)

    service.delete(maria.id, current_user_id=admin.id)

    assert [user.email for user in service.list_all()] == ["admin@library.gr"]


def test_admin_cannot_delete_themselves(service):
    admin = service.create("Admin", "admin@library.gr", "123456",
                           User.ROLE_ADMIN)

    with pytest.raises(ServiceError, match="εαυτό"):
        service.delete(admin.id, current_user_id=admin.id)


def test_cannot_delete_user_with_loans(service, maria, db_path):
    book = BookDAO(db_path).add(Book("1984", "George Orwell", 1949, "978-2"))
    today = date(2026, 10, 1)
    LoanDAO(db_path).add(
        Loan(book.id, maria.id, today, today + timedelta(days=14))
    )

    with pytest.raises(ServiceError, match="δανεισμούς"):
        service.delete(maria.id, current_user_id=999)

    assert service.get(maria.id).name == "Μαρία"


def test_delete_missing_user_fails(service):
    with pytest.raises(ServiceError, match="δεν βρέθηκε"):
        service.delete(999, current_user_id=1)