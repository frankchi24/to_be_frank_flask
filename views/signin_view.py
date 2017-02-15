# -*- coding: utf-8 -*-
from flask import Flask, request, session, redirect, url_for, Blueprint, flash, render_template, jsonify, send_file, send_from_directory
from passlib.hash import sha256_crypt
from MySQLdb import escape_string as thwart
from FlaskApp.util import admin_required, login_required
from FlaskApp.models import users, db
from FlaskApp.forms import RegistrationForm

signin_view = Blueprint('signin_view', __name__)

@signin_view.route('/login/', methods=['GET', 'POST'])
def login():
    error = ''
    try:
        if request.method == "POST":
            user = users.query.filter_by(username = thwart(request.form['username'])).first()
            data = user.password
            if sha256_crypt.verify(request.form['password'], data):
                session['logged_in'] = True
                session['username'] = request.form['username']
                flash("You are logged in")
                if request.form['username'] == 'admin':
                    session['admin'] = True

                return redirect(url_for('blog.homepage'))
            else:
                error = "Invalid credentials, try again"
                flash(error)
        return redirect(url_for('blog.homepage'))

    except Exception as e:
        error = "Invalid credentials, try again"
        flash(error)
        return redirect(url_for('blog.homepage'))


@signin_view.route("/logout/")
@login_required
def logout():
    session.clear()
    flash("You have been logged out")
    return redirect(url_for('blog.homepage'))


@signin_view.route('/register/', methods=["GET", "POST"])
def register_page():
    try:
        form = RegistrationForm(request.form)
        if request.method == "POST" and form.validate():
            username = form.username.data
            email = form.email.data
            password = sha256_crypt.encrypt((str(form.password.data)))
            exist_user = users.query.filter_by(username = username).first()

            if exist_user != None:
                flash("That username is already taken, please choose another")
                return render_template('register.html', form=form)

            else:
                new_user = users(thwart(username),thwart(password),thwart(email),)

                db.session.add(new_user)
                db.session.commit()
                flash("Thanks for registering!")
                session['logged_in'] = True
                session['username'] = username

                return redirect(url_for('blog.homepage'))

        return render_template("register.html", form=form)

    except Exception as e:
        return(str(e))

