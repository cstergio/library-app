import sqlite3

import pytest

from dao.user_dao import UserDAO
from models.user import User


@pytest.fixture
def dao(db_path):
    return UserDAO(db_path)


def make_user(name="Μαρία", email="maria@example.com", role=User.ROLE_USER):
    return User(name, email, "hash", role)


def test_add_gives_the_user_an_id(dao):
    user = dao.add(make_user())
    assert user.id is not None


def test_added_user_can_be_found_by_id(dao):
    added = dao.add(make_user())

    found = dao.get_by_id(added.id)

    assert found.name == "Μαρία"
    assert found.email == "maria@example.com"
    assert found.password_hash == "hash"
    assert found.role == User.ROLE_USER


def test_get_by_id_returns_none_when_missing(dao):
    assert dao.get_by_id(999) is None


def test_user_can_be_found_by_email(dao):
    added = dao.add(make_user())

    found = dao.get_by_email("maria@example.com")

    assert found.id == added.id


def test_get_by_email_returns_none_when_missing(dao):
    assert dao.get_by_email("kanenas@example.com") is None


def test_admin_role_is_saved(dao):
    added = dao.add(make_user("Admin", "admin@library.gr", User.ROLE_ADMIN))

    found = dao.get_by_id(added.id)

    assert found.is_admin() is True


def test_get_all_returns_users_sorted_by_name(dao):
    dao.add(make_user("Νίκος", "nikos@example.com"))
    dao.add(make_user("Άννα", "anna@example.com"))
    dao.add(make_user("Γιώργος", "giorgos@example.com"))

    names = [user.name for user in dao.get_all()]

    assert names == ["Άννα", "Γιώργος", "Νίκος"]


def test_update_changes_the_user(dao):
    user = dao.add(make_user())

    user.name = "Μαρία Παπαδοπούλου"
    user.role = User.ROLE_ADMIN
    dao.update(user)

    found = dao.get_by_id(user.id)
    assert found.name == "Μαρία Παπαδοπούλου"
    assert found.is_admin() is True


def test_delete_removes_the_user(dao):
    user = dao.add(make_user())

    dao.delete(user.id)

    assert dao.get_by_id(user.id) is None


def test_add_with_same_email_fails(dao):
    dao.add(make_user("Μαρία", "maria@example.com"))

    with pytest.raises(sqlite3.IntegrityError):
        dao.add(make_user("Άλλη Μαρία", "maria@example.com"))