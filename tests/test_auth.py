# ---------- βοηθητικές ----------

def register(client, email="maria@example.com", password="123456"):
    return client.post("/register", data={
        "name": "Μαρία",
        "email": email,
        "password": password,
    })


def login(client, email="maria@example.com", password="123456"):
    return client.post("/login", data={
        "email": email,
        "password": password,
    }, follow_redirects=True)


# ---------- εγγραφή ----------

def test_register_page_opens(client):
    response = client.get("/register")

    assert response.status_code == 200
    assert "Εγγραφή" in response.get_data(as_text=True)


def test_successful_register_redirects_to_login(client):
    response = register(client)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")


def test_successful_register_creates_the_user(client, app):
    register(client)

    user = app.user_service.authenticate("maria@example.com", "123456")
    assert user.name == "Μαρία"


def test_successful_register_shows_message(client):
    response = client.post("/register", data={
        "name": "Μαρία",
        "email": "maria@example.com",
        "password": "123456",
    }, follow_redirects=True)

    assert "Η εγγραφή ολοκληρώθηκε" in response.get_data(as_text=True)


def test_failed_register_shows_error_and_keeps_data(client, app):
    response = register(client, password="123")

    page = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "κωδικός" in page
    assert 'value="maria@example.com"' in page
    assert app.user_service.list_all() == []


# ---------- σύνδεση ----------

def test_login_page_opens(client):
    response = client.get("/login")

    assert response.status_code == 200
    assert "Σύνδεση" in response.get_data(as_text=True)


def test_visitor_sees_login_and_register_links(client):
    page = client.get("/").get_data(as_text=True)

    assert "Σύνδεση" in page
    assert "Εγγραφή" in page
    assert "Αποσύνδεση" not in page


def test_successful_login_shows_the_user(client):
    register(client)

    page = login(client).get_data(as_text=True)

    assert "Καλώς ήρθατε, Μαρία!" in page
    assert "Αποσύνδεση" in page


def test_user_stays_logged_in_on_next_page(client):
    register(client)
    login(client)

    page = client.get("/").get_data(as_text=True)

    assert "Αποσύνδεση" in page


def test_wrong_password_shows_error_and_keeps_email(client):
    register(client)

    page = login(client, password="λάθος").get_data(as_text=True)

    assert "Λάθος email ή κωδικός" in page
    assert 'value="maria@example.com"' in page
    assert "Αποσύνδεση" not in page


# ---------- αποσύνδεση ----------

def test_logout_logs_the_user_out(client):
    register(client)
    login(client)

    page = client.get("/logout", follow_redirects=True).get_data(as_text=True)

    assert "Αποσυνδεθήκατε" in page
    assert "Αποσύνδεση" not in page
    assert "Σύνδεση" in page