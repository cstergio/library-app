class User:
    """Ένας χρήστης της εφαρμογής, απλός χρήστης ή διαχειριστής."""

    ROLE_ADMIN = "admin"
    ROLE_USER = "user"

    def __init__(self, name, email, password_hash, role=ROLE_USER, id=None):
        self.id = id
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.role = role

    def is_admin(self):
        return self.role == User.ROLE_ADMIN

    def __str__(self):
        return f"{self.name} <{self.email}> [{self.role}]"