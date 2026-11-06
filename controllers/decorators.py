from functools import wraps

from flask import flash, g, redirect, url_for


def login_required(view):
    """Η σελίδα ανοίγει μόνο σε συνδεδεμένους χρήστες."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            flash("Πρέπει να συνδεθείτε πρώτα.", "error")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped