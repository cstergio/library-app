from flask import (Blueprint, current_app, flash, g, redirect,
                   render_template, request, session, url_for)

from services.errors import ServiceError

auth = Blueprint("auth", __name__)


# ---------- ποιος είναι συνδεδεμένος ----------

@auth.before_app_request
def load_current_user():
    g.user = None
    user_id = session.get("user_id")

    if user_id is not None:
        try:
            g.user = current_app.user_service.get(user_id)
        except ServiceError:
            session.clear()


# ---------- εγγραφή ----------

@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "")
        email = request.form.get("email", "")
        password = request.form.get("password", "")

        try:
            current_app.user_service.register(name, email, password)
        except ServiceError as error:
            flash(str(error), "error")
            return render_template("auth/register.html",
                                   name=name, email=email)

        flash("Η εγγραφή ολοκληρώθηκε. Μπορείτε τώρα να συνδεθείτε.",
              "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", name="", email="")


# ---------- σύνδεση ----------

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "")
        password = request.form.get("password", "")

        try:
            user = current_app.user_service.authenticate(email, password)
        except ServiceError as error:
            flash(str(error), "error")
            return render_template("auth/login.html", email=email)

        session.clear()
        session["user_id"] = user.id
        flash(f"Καλώς ήρθατε, {user.name}!", "success")
        if user.is_admin():
            return redirect(url_for("admin.books"))
        return redirect(url_for("user.books"))

    return render_template("auth/login.html", email="")


# ---------- αποσύνδεση ----------

@auth.route("/logout")
def logout():
    session.clear()
    flash("Αποσυνδεθήκατε.", "success")
    return redirect(url_for("home"))