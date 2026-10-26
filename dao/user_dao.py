from database import DB_PATH, get_connection
from models.user import User


class UserDAO:
    """Αποθήκευση και ανάγνωση χρηστών από τη βάση."""

    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path

    def add(self, user):
        conn = get_connection(self.db_path)
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash, role) "
            "VALUES (?, ?, ?, ?)",
            (user.name, user.email, user.password_hash, user.role),
        )
        conn.commit()
        user.id = cursor.lastrowid
        conn.close()
        return user

    def get_by_id(self, user_id):
        conn = get_connection(self.db_path)
        row = conn.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        conn.close()
        if row is None:
            return None
        return self._row_to_user(row)

    def get_by_email(self, email):
        conn = get_connection(self.db_path)
        row = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
        conn.close()
        if row is None:
            return None
        return self._row_to_user(row)

    def get_all(self):
        conn = get_connection(self.db_path)
        rows = conn.execute("SELECT * FROM users ORDER BY name").fetchall()
        conn.close()
        return [self._row_to_user(row) for row in rows]

    def update(self, user):
        conn = get_connection(self.db_path)
        conn.execute(
            "UPDATE users SET name = ?, email = ?, password_hash = ?, role = ? "
            "WHERE id = ?",
            (user.name, user.email, user.password_hash, user.role, user.id),
        )
        conn.commit()
        conn.close()

    def delete(self, user_id):
        conn = get_connection(self.db_path)
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()

    def _row_to_user(self, row):
        return User(
            id=row["id"],
            name=row["name"],
            email=row["email"],
            password_hash=row["password_hash"],
            role=row["role"],
        )