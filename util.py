from functools import wraps
from flask import flash, redirect, url_for, session


def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'admin' == session['username']:
            return f(*args, **kwargs)
        else:
            flash("You are not admin")
            return redirect(url_for('homepage'))
    return wrap


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('login'))
    return wrap
