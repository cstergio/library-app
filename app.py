from flask import Flask, render_template

from controllers.admin_controller import admin
from controllers.auth_controller import auth
from controllers.user_controller import user
from dao.book_dao import BookDAO
from dao.loan_dao import LoanDAO
from dao.user_dao import UserDAO
from database import DB_PATH, init_db
from services.book_service import BookService
from services.loan_service import LoanService
from services.user_service import UserService


def create_app(db_path=DB_PATH):
    """Φτιάχνει και ρυθμίζει την εφαρμογή."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "allaxe-me-se-pragmatiko-server"

    init_db(db_path)

    book_dao = BookDAO(db_path)
    user_dao = UserDAO(db_path)
    loan_dao = LoanDAO(db_path)

    app.book_service = BookService(book_dao, loan_dao)
    app.user_service = UserService(user_dao, loan_dao)
    app.loan_service = LoanService(loan_dao, book_dao)

    @app.route("/")
    def home():
        return render_template("home.html")

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("403.html"), 403

    app.register_blueprint(auth)
    app.register_blueprint(user)
    app.register_blueprint(admin)

    return app


if __name__ == "__main__":
    create_app().run(debug=True)