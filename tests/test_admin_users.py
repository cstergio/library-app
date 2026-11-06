USER_FORM = {
    "name": "Νίκος",
    "email": "nikos@example.com",
    "password": "123456",
    "role": "user",
}


# ---------- κλείδωμα ----------

def test_visitor_is_sent_to_login(client):
    response = client.get("/admin/users")

    assert response.headers["Location"].endswith("/login")


def test_simple_user_gets_403(maria_client):
    response = maria_client.get("/admin/users")

    assert response.status_code == 403


def test_simple_user_cannot_create_users(maria_client, app):
    data = dict(USER_FORM, role="admin")

    response = maria_client.post("/admin/users/new", data=data)

    assert response.status_code == 403
    assert len(app.user_service.list_all()) == 1


# ---------- λίστα ----------

def test_admin_sees_all_users(admin_client, maria):
    page = admin_client.get("/admin/users").get_data(as_text=True)

    assert "maria@example.com" in page
    assert "admin@library.gr" in page
    assert "Διαχειριστής" in page


def test_admin_has_no_delete_button_for_self(admin_client, admin_user):
    page = admin_client.get("/admin/users").get_data(as_text=True)

    assert f"/admin/users/{admin_user.id}/delete" not in page


# ---------- νέος χρήστης ----------

def test_new_user_form_opens(admin_client):
    response = admin_client.get("/admin/users/new")

    assert response.status_code == 200
    assert "Νέος χρήστης" in response.get_data(as_text=True)


def test_admin_creates_a_user(admin_client, app):
    response = admin_client.post("/admin/users/new", data=USER_FORM,
                                 follow_redirects=True)

    assert "Ο χρήστης δημιουργήθηκε" in response.get_data(as_text=True)
    user = app.user_service.authenticate("nikos@example.com", "123456")
    assert user.is_admin() is False


def test_admin_creates_another_admin(admin_client, app):
    admin_client.post("/admin/users/new", data=dict(USER_FORM, role="admin"))

    user = app.user_service.authenticate("nikos@example.com", "123456")
    assert user.is_admin() is True


def test_new_user_error_keeps_the_data(admin_client, app):
    data = dict(USER_FORM, password="123")

    page = admin_client.post("/admin/users/new", data=data).get_data(as_text=True)

    assert "κωδικός" in page
    assert 'value="nikos@example.com"' in page
    assert len(app.user_service.list_all()) == 1


# ---------- αλλαγή ----------

def test_edit_form_is_filled(admin_client, maria):
    page = admin_client.get(f"/admin/users/{maria.id}/edit").get_data(as_text=True)

    assert 'value="Μαρία"' in page
    assert 'value="maria@example.com"' in page


def test_admin_makes_user_admin(admin_client, app, maria):
    admin_client.post(f"/admin/users/{maria.id}/edit", data={
        "name": "Μαρία",
        "email": "maria@example.com",
        "role": "admin",
        "password": "",
    })

    assert app.user_service.get(maria.id).is_admin() is True


def test_edit_without_password_keeps_it(admin_client, app, maria):
    admin_client.post(f"/admin/users/{maria.id}/edit", data={
        "name": "Μαρία Π.",
        "email": "maria@example.com",
        "role": "user",
        "password": "",
    })

    user = app.user_service.authenticate("maria@example.com", "123456")
    assert user.name == "Μαρία Π."


def test_edit_with_new_password_changes_it(admin_client, app, maria):
    admin_client.post(f"/admin/users/{maria.id}/edit", data={
        "name": "Μαρία",
        "email": "maria@example.com",
        "role": "user",
        "password": "neos-kodikos",
    })

    user = app.user_service.authenticate("maria@example.com", "neos-kodikos")
    assert user.id == maria.id


def test_edit_missing_user_shows_error(admin_client):
    response = admin_client.get("/admin/users/999/edit", follow_redirects=True)

    assert "δεν βρέθηκε" in response.get_data(as_text=True)


# ---------- διαγραφή ----------

def test_admin_deletes_a_user(admin_client, app, maria):
    response = admin_client.post(f"/admin/users/{maria.id}/delete",
                                 follow_redirects=True)

    assert "Ο χρήστης διαγράφηκε" in response.get_data(as_text=True)
    assert [u.email for u in app.user_service.list_all()] == ["admin@library.gr"]


def test_admin_cannot_delete_self(admin_client, app, admin_user):
    response = admin_client.post(f"/admin/users/{admin_user.id}/delete",
                                 follow_redirects=True)

    assert "εαυτό" in response.get_data(as_text=True)
    assert len(app.user_service.list_all()) == 1


def test_cannot_delete_user_with_loans(admin_client, app, maria):
    book = app.book_service.create("1984", "George Orwell", "1949", "978-2")
    app.loan_service.borrow(maria.id, book.id)

    response = admin_client.post(f"/admin/users/{maria.id}/delete",
                                 follow_redirects=True)

    assert "δανεισμούς" in response.get_data(as_text=True)
    assert app.user_service.get(maria.id).name == "Μαρία"