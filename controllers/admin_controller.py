from flask import (Blueprint, current_app, flash, redirect,
                   render_template, request, url_for)

from controllers.decorators import admin_required
from services.errors import ServiceError

admin = Blueprint("admin", __name__, url_prefix="/admin")


# ---------- λίστα βιβλίων ----------

@admin.route("/books")
@admin_required
def books():
    all_books = current_app.book_service.list_all()
    available_ids = {book.id for book in current_app.book_service.list_available()}
    return render_template("admin/books.html",
                           books=all_books, available_ids=available_ids)


# ---------- νέο βιβλίο ----------

@admin.route("/books/new", methods=["GET", "POST"])
@admin_required
def new_book():
    if request.method == "POST":
        form = request.form
        try:
            current_app.book_service.create(
                form.get("title"), form.get("author"),
                form.get("year"), form.get("isbn"),
            )
        except ServiceError as error:
            flash(str(error), "error")
            return render_template("admin/book_form.html",
                                   heading="Νέο βιβλίο", book=form)

        flash("Το βιβλίο προστέθηκε.", "success")
        return redirect(url_for("admin.books"))

    return render_template("admin/book_form.html",
                           heading="Νέο βιβλίο", book={})


# ---------- αλλαγή βιβλίου ----------

@admin.route("/books/<int:book_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_book(book_id):
    try:
        book = current_app.book_service.get(book_id)
    except ServiceError as error:
        flash(str(error), "error")
        return redirect(url_for("admin.books"))

    if request.method == "POST":
        form = request.form
        try:
            current_app.book_service.update(
                book_id, form.get("title"), form.get("author"),
                form.get("year"), form.get("isbn"),
            )
        except ServiceError as error:
            flash(str(error), "error")
            return render_template("admin/book_form.html",
                                   heading="Αλλαγή βιβλίου", book=form)

        flash("Το βιβλίο αποθηκεύτηκε.", "success")
        return redirect(url_for("admin.books"))

    return render_template("admin/book_form.html",
                           heading="Αλλαγή βιβλίου", book=book)


# ---------- διαγραφή βιβλίου ----------

@admin.route("/books/<int:book_id>/delete", methods=["POST"])
@admin_required
def delete_book(book_id):
    try:
        current_app.book_service.delete(book_id)
    except ServiceError as error:
        flash(str(error), "error")
    else:
        flash("Το βιβλίο διαγράφηκε.", "success")

    return redirect(url_for("admin.books"))