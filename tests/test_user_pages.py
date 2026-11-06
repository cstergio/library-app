# ---------- κλείδωμα ----------

def test_visitor_is_sent_to_login(client):
    response = client.get("/books")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")


def test_visitor_sees_why(client):
    page = client.get("/books", follow_redirects=True).get_data(as_text=True)

    assert "Πρέπει να συνδεθείτε" in page


def test_login_goes_to_books(client, maria):
    response = client.post("/login", data={
        "email": "maria@example.com",
        "password": "123456",
    })

    assert response.headers["Location"].endswith("/books")


# ---------- διαθέσιμα βιβλία ----------

def test_user_sees_available_books(maria_client, app):
    app.book_service.create("1984", "George Orwell", "1949", "978-2")

    page = maria_client.get("/books").get_data(as_text=True)

    assert "1984" in page
    assert "George Orwell" in page


def test_empty_list_shows_message(maria_client):
    page = maria_client.get("/books").get_data(as_text=True)

    assert "Δεν υπάρχουν διαθέσιμα βιβλία" in page


def test_loaned_book_is_not_listed(maria_client, app):
    book = app.book_service.create("1984", "George Orwell", "1949", "978-2")
    nikos = app.user_service.register("Νίκος", "nikos@example.com", "123456")
    app.loan_service.borrow(nikos.id, book.id)

    page = maria_client.get("/books").get_data(as_text=True)

    assert "1984" not in page


# ---------- δανεισμός ----------

def test_borrow_creates_a_loan(maria_client, app, maria):
    book = app.book_service.create("1984", "George Orwell", "1949", "978-2")

    maria_client.post(f"/books/{book.id}/borrow")

    loans = app.loan_service.active_loans(maria.id)
    assert [loan.book_title for loan in loans] == ["1984"]


def test_borrow_shows_success_message(maria_client, app):
    book = app.book_service.create("1984", "George Orwell", "1949", "978-2")

    response = maria_client.post(f"/books/{book.id}/borrow",
                                 follow_redirects=True)

    assert "Δανειστήκατε το «1984»" in response.get_data(as_text=True)


def test_borrow_shows_service_error(maria_client, app):
    book = app.book_service.create("1984", "George Orwell", "1949", "978-2")
    nikos = app.user_service.register("Νίκος", "nikos@example.com", "123456")
    app.loan_service.borrow(nikos.id, book.id)

    response = maria_client.post(f"/books/{book.id}/borrow",
                                 follow_redirects=True)

    assert "ήδη δανεισμένο" in response.get_data(as_text=True)


def test_borrow_with_get_is_not_allowed(maria_client, app):
    book = app.book_service.create("1984", "George Orwell", "1949", "978-2")

    response = maria_client.get(f"/books/{book.id}/borrow")

    assert response.status_code == 405


def test_visitor_cannot_borrow(client, app):
    book = app.book_service.create("1984", "George Orwell", "1949", "978-2")

    response = client.post(f"/books/{book.id}/borrow")

    assert response.headers["Location"].endswith("/login")
    assert app.book_service.list_available()[0].title == "1984"


# ---------- τα βιβλία μου ----------

def test_visitor_cannot_see_my_loans(client):
    response = client.get("/my/loans")

    assert response.headers["Location"].endswith("/login")


def test_my_loans_empty_shows_message(maria_client):
    page = maria_client.get("/my/loans").get_data(as_text=True)

    assert "Δεν έχετε δανεισμένα βιβλία" in page


def test_my_loans_shows_title_and_due_date(maria_client, app, maria):
    book = app.book_service.create("1984", "George Orwell", "1949", "978-2")
    loan = app.loan_service.borrow(maria.id, book.id)

    page = maria_client.get("/my/loans").get_data(as_text=True)

    assert "1984" in page
    assert loan.due_date.strftime("%d/%m/%Y") in page


def test_my_loans_shows_only_my_books(maria_client, app):
    book = app.book_service.create("1984", "George Orwell", "1949", "978-2")
    nikos = app.user_service.register("Νίκος", "nikos@example.com", "123456")
    app.loan_service.borrow(nikos.id, book.id)

    page = maria_client.get("/my/loans").get_data(as_text=True)

    assert "1984" not in page


# ---------- επιστροφή ----------

def test_return_ends_the_loan(maria_client, app, maria):
    book = app.book_service.create("1984", "George Orwell", "1949", "978-2")
    loan = app.loan_service.borrow(maria.id, book.id)

    response = maria_client.post(f"/my/loans/{loan.id}/return",
                                 follow_redirects=True)

    assert "Επιστρέψατε το «1984»" in response.get_data(as_text=True)
    assert app.loan_service.active_loans(maria.id) == []
    assert app.book_service.list_available()[0].title == "1984"


def test_cannot_return_someone_elses_book(maria_client, app):
    book = app.book_service.create("1984", "George Orwell", "1949", "978-2")
    nikos = app.user_service.register("Νίκος", "nikos@example.com", "123456")
    loan = app.loan_service.borrow(nikos.id, book.id)

    response = maria_client.post(f"/my/loans/{loan.id}/return",
                                 follow_redirects=True)

    assert "δεν βρέθηκε" in response.get_data(as_text=True)
    assert len(app.loan_service.active_loans(nikos.id)) == 1


def test_return_with_get_is_not_allowed(maria_client, app, maria):
    book = app.book_service.create("1984", "George Orwell", "1949", "978-2")
    loan = app.loan_service.borrow(maria.id, book.id)

    response = maria_client.get(f"/my/loans/{loan.id}/return")

    assert response.status_code == 405



# ---------- ιστορικό ----------

def test_visitor_cannot_see_history(client):
    response = client.get("/my/history")

    assert response.headers["Location"].endswith("/login")


def test_empty_history_shows_message(maria_client):
    page = maria_client.get("/my/history").get_data(as_text=True)

    assert "Δεν έχετε δανειστεί ακόμα" in page


def test_history_shows_active_and_returned_loans(maria_client, app, maria):
    first = app.book_service.create("1984", "George Orwell", "1949", "978-2")
    second = app.book_service.create("Ζορμπάς", "Νίκος Καζαντζάκης",
                                     "1946", "978-5")
    loan = app.loan_service.borrow(maria.id, first.id)
    app.loan_service.return_book(maria.id, loan.id)
    app.loan_service.borrow(maria.id, second.id)

    page = maria_client.get("/my/history").get_data(as_text=True)

    assert "1984" in page
    assert "Ζορμπάς" in page
    assert "ενεργός" in page


def test_history_shows_only_my_loans(maria_client, app):
    book = app.book_service.create("1984", "George Orwell", "1949", "978-2")
    nikos = app.user_service.register("Νίκος", "nikos@example.com", "123456")
    app.loan_service.borrow(nikos.id, book.id)

    page = maria_client.get("/my/history").get_data(as_text=True)

    assert "1984" not in page