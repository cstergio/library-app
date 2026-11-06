import pytest

from app import create_app
from database import init_db


@pytest.fixture
def db_path(tmp_path):
    """Μια καινούργια, άδεια βάση για κάθε test."""
    path = tmp_path / "test.db"
    init_db(path)
    return path


@pytest.fixture
def app(db_path):
    """Η εφαρμογή, συνδεδεμένη με την προσωρινή βάση."""
    app = create_app(db_path)
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    """Ένας ψεύτικος browser για να ανοίγουμε σελίδες στα tests."""
    return app.test_client()


@pytest.fixture
def maria(app):
    """Μια εγγεγραμμένη χρήστρια."""
    return app.user_service.register("Μαρία", "maria@example.com", "123456")


@pytest.fixture
def maria_client(client, maria):
    """Ψεύτικος browser όπου η Μαρία είναι ήδη συνδεδεμένη."""
    client.post("/login", data={
        "email": "maria@example.com",
        "password": "123456",
    })
    return client