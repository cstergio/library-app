from werkzeug.security import check_password_hash, generate_password_hash

from models.user import User
from services.errors import ServiceError

MIN_PASSWORD_LENGTH = 6
VALID_ROLES = (User.ROLE_ADMIN, User.ROLE_USER)


class UserService:
    """Οι κανόνες για τους χρήστες, εγγραφή, σύνδεση, διαχείριση."""

    def __init__(self, user_dao, loan_dao):
        self.user_dao = user_dao
        self.loan_dao = loan_dao

    # ---------- εγγραφή και σύνδεση ----------

    def register(self, name, email, password):
        return self._create(name, email, password, User.ROLE_USER)

    def authenticate(self, email, password):
        email = (email or "").strip().lower()
        user = self.user_dao.get_by_email(email)

        if user is None or not check_password_hash(user.password_hash,
                                                   password or ""):
            raise ServiceError("Λάθος email ή κωδικός.")

        return user

    # ---------- ανάγνωση ----------

    def list_all(self):
        return self.user_dao.get_all()

    def get(self, user_id):
        user = self.user_dao.get_by_id(user_id)
        if user is None:
            raise ServiceError("Ο χρήστης δεν βρέθηκε.")
        return user

    # ---------- διαχείριση από τον admin ----------

    def create(self, name, email, password, role):
        return self._create(name, email, password, role)

    def update(self, user_id, name, email, role, new_password=None):
        user = self.get(user_id)
        name = self._clean_name(name)
        email = self._clean_email(email)
        self._check_role(role)

        other = self.user_dao.get_by_email(email)
        if other is not None and other.id != user.id:
            raise ServiceError("Το email χρησιμοποιείται ήδη.")

        user.name = name
        user.email = email
        user.role = role

        if new_password:
            self._check_password(new_password)
            user.password_hash = generate_password_hash(new_password)

        self.user_dao.update(user)
        return user

    def delete(self, user_id, current_user_id):
        user = self.get(user_id)

        if user.id == current_user_id:
            raise ServiceError("Δεν μπορείτε να διαγράψετε τον εαυτό σας.")

        if self.loan_dao.user_has_loans(user.id):
            raise ServiceError(
                "Ο χρήστης έχει δανεισμούς και δεν μπορεί να διαγραφεί."
            )

        self.user_dao.delete(user.id)

    # ---------- βοηθητικές ----------

    def _create(self, name, email, password, role):
        name = self._clean_name(name)
        email = self._clean_email(email)
        self._check_password(password)
        self._check_role(role)

        if self.user_dao.get_by_email(email) is not None:
            raise ServiceError("Το email χρησιμοποιείται ήδη.")

        user = User(name, email, generate_password_hash(password), role)
        return self.user_dao.add(user)

    def _clean_name(self, name):
        name = (name or "").strip()
        if not name:
            raise ServiceError("Το όνομα είναι υποχρεωτικό.")
        return name

    def _clean_email(self, email):
        email = (email or "").strip().lower()
        if not email:
            raise ServiceError("Το email είναι υποχρεωτικό.")
        if "@" not in email or email.startswith("@") or email.endswith("@"):
            raise ServiceError("Το email δεν είναι έγκυρο.")
        return email

    def _check_password(self, password):
        if not password or len(password) < MIN_PASSWORD_LENGTH:
            raise ServiceError(
                f"Ο κωδικός πρέπει να έχει τουλάχιστον "
                f"{MIN_PASSWORD_LENGTH} χαρακτήρες."
            )

    def _check_role(self, role):
        if role not in VALID_ROLES:
            raise ServiceError("Μη έγκυρος ρόλος.")