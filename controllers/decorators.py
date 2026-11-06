from functools import wraps

from flask import abort, flash, g, redirect, url_for


def login_required(view):
    """Η σελίδα ανοίγει μόνο σε συνδεδεμένους χρήστες."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            flash("Πρέπει να συνδεθείτε πρώτα.", "error")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped


def admin_required(view):
    """Η σελίδα ανοίγει μόνο στον διαχειριστή."""

    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not g.user.is_admin():
            abort(403)
        return view(*args, **kwargs)

    return wrapped