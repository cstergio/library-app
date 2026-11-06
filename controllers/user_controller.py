from flask import (Blueprint, current_app, flash, g, redirect,
                   render_template, url_for)

from controllers.decorators import login_required
from services.errors import ServiceError

user = Blueprint("user", __name__)


# ---------- διαθέσιμα βιβλία και δανεισμός ----------

@user.route("/books")
@login_required
def books():
    available = current_app.book_service.list_available()
    return render_template("user/books.html", books=available)


@user.route("/books/<int:book_id>/borrow", methods=["POST"])
@login_required
def borrow(book_id):
    try:
        loan = current_app.loan_service.borrow(g.user.id, book_id)
    except ServiceError as error:
        flash(str(error), "error")
    else:
        due = loan.due_date.strftime("%d/%m/%Y")
        flash(f"Δανειστήκατε το «{loan.book_title}». Επιστροφή έως {due}.",
              "success")

    return redirect(url_for("user.books"))


# ---------- τα βιβλία μου και επιστροφή ----------

@user.route("/my/loans")
@login_required
def my_loans():
    loans = current_app.loan_service.active_loans(g.user.id)
    return render_template("user/my_loans.html", loans=loans)


@user.route("/my/loans/<int:loan_id>/return", methods=["POST"])
@login_required
def return_loan(loan_id):
    try:
        loan = current_app.loan_service.return_book(g.user.id, loan_id)
    except ServiceError as error:
        flash(str(error), "error")
    else:
        flash(f"Επιστρέψατε το «{loan.book_title}». Ευχαριστούμε!",
              "success")

    return redirect(url_for("user.my_loans"))



# ---------- ιστορικό ----------

@user.route("/my/history")
@login_required
def history():
    loans = current_app.loan_service.history(g.user.id)
    return render_template("user/history.html", loans=loans)