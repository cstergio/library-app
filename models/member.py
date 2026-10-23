class Member:
    """Ένα μέλος της βιβλιοθήκης."""

    def __init__(self, name, email, id=None):
        self.id = id
        self.name = name
        self.email = email

    def __str__(self):
        return f"{self.name} <{self.email}>"