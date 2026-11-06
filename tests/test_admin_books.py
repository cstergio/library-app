BOOK_FORM = {
    "title": "1984",
    "author": "George Orwell",
    "year": "1949",
    "isbn": "978-2",
}


# ---------- κλείδωμα ----------

def test_visitor_is_sent_to_login(client):
    response = client.get("/admin/books")

    assert response.headers["Location"].endswith("/login")


def test_simple_user_gets_403(maria_client):
    response = maria_client.get("/admin/books")

    assert response.status_code == 403
    assert "Δεν έχετε δικαίωμα" in response.get_data(as_text=True)


def test_simple_user_cannot_add_book(maria_client, app):
    response = maria_client.post("/admin/books/new", data=BOOK_FORM)

    assert response.status_code == 403
    assert app.book_service.list_all() == []


def test_admin_login_goes_to_admin_books(client, admin_user):
    response = client.post("/login", data={
        "email": "admin@library.gr",
        "password": "123456",
    })

    assert response.headers["Location"].endswith("/admin/books")


# ---------- λίστα ----------

def test_admin_sees_all_books_with_status(admin_client, app, maria):
    loaned = app.book_service.create("1984", "George Orwell", "1949", "978-2")
    app.book_service.create("Ζορμπάς", "Νίκος Καζαντζάκης", "1946", "978-5")
    app.loan_service.borrow(maria.id, loaned.id)

    page = admin_client.get("/admin/books").get_data(as_text=True)

    assert "1984" in page
    assert "Ζορμπάς" in page
    assert "Δανεισμένο" in page
    assert "Διαθέσιμο" in page


# ---------- νέο βιβλίο ----------

def test_new_book_form_opens(admin_client):
    response = admin_client.get("/admin/books/new")

    assert response.status_code == 200
    assert "Νέο βιβλίο" in response.get_data(as_text=True)


def test_admin_adds_a_book(admin_client, app):
    response = admin_client.post("/admin/books/new", data=BOOK_FORM,
                                 follow_redirects=True)

    assert "Το βιβλίο προστέθηκε" in response.get_data(as_text=True)
    assert [book.title for book in app.book_service.list_all()] == ["1984"]


def test_new_book_error_keeps_the_data(admin_client, app):
    data = dict(BOOK_FORM, title="")

    response = admin_client.post("/admin/books/new", data=data)

    page = response.get_data(as_text=True)
    assert "τίτλος" in page
    assert 'value="George Orwell"' in page
    assert app.book_service.list_all() == []


# ---------- αλλαγή ----------

def test_edit_form_is_filled(admin_client, app):
    book = app.book_service.create("1984", "George Orwell", "1949", "978-2")

    page = admin_client.get(f"/admin/books/{book.id}/edit").get_data(as_text=True)

    assert 'value="1984"' in page
    assert 'value="George Orwell"' in page


def test_admin_edits_a_book(admin_client, app):
    book = app.book_service.create("1984", "George Orwell", "1949", "978-2")
    data = dict(BOOK_FORM, title="Νέος τίτλος")

    admin_client.post(f"/admin/books/{book.id}/edit", data=data)

    assert app.book_service.get(book.id).title == "Νέος τίτλος"


def test_edit_missing_book_shows_error(admin_client):
    response = admin_client.get("/admin/books/999/edit", follow_redirects=True)

    assert "δεν βρέθηκε" in response.get_data(as_text=True)


# ---------- διαγραφή ----------

def test_admin_deletes_a_book(admin_client, app):
    book = app.book_service.create("1984", "George Orwell", "1949", "978-2")

    response = admin_client.post(f"/admin/books/{book.id}/delete",
                                 follow_redirects=True)

    assert "Το βιβλίο διαγράφηκε" in response.get_data(as_text=True)
    assert app.book_service.list_all() == []


def test_cannot_delete_book_with_loans(admin_client, app, maria):
    book = app.book_service.create("1984", "George Orwell", "1949", "978-2")
    app.loan_service.borrow(maria.id, book.id)

    response = admin_client.post(f"/admin/books/{book.id}/delete",
                                 follow_redirects=True)

    assert "δανεισμούς" in response.get_data(as_text=True)
    assert len(app.book_service.list_all()) == 1


def test_delete_with_get_is_not_allowed(admin_client, app):
    book = app.book_service.create("1984", "George Orwell", "1949", "978-2")

    response = admin_client.get(f"/admin/books/{book.id}/delete")

    assert response.status_code == 405