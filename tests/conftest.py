import pytest

from database import init_db


@pytest.fixture
def db_path(tmp_path):
    """Μια καινούργια, άδεια βάση για κάθε test."""
    path = tmp_path / "test.db"
    init_db(path)
    return path