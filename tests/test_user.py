from models.user import User


def test_new_user_is_simple_user_by_default():
    user = User("Μαρία", "maria@example.com", "hash")
    assert user.role == User.ROLE_USER
    assert user.is_admin() is False


def test_admin_user():
    user = User("Διαχειριστής", "admin@library.gr", "hash", User.ROLE_ADMIN)
    assert user.is_admin() is True


def test_new_user_has_no_id():
    user = User("Μαρία", "maria@example.com", "hash")
    assert user.id is None


def test_user_as_text():
    user = User("Μαρία", "maria@example.com", "hash")
    assert str(user) == "Μαρία <maria@example.com> [user]"