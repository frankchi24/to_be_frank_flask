# -*- coding: utf-8 -*-
from flask import Flask, render_template, flash, session, request, url_for, redirect
from dbconnect import connection, connection_scripts
from passlib.hash import sha256_crypt
from MySQLdb import escape_string as thwart
import gc
import os
from flask_mail import Mail, Message
from util import admin_required, login_required
from forms import *


app = Flask(
    __name__, instance_relative_config=True,
    instance_path='/Users/Mac/Downloads/Coding/flask/FlaskApp/instance')
app.config.from_object('config')
app.config.from_pyfile('config.py')
mail = Mail(app)
pagedown = PageDown(app)

# cache = Cache(app, config={'CACHE_TYPE': 'simple'})
# cache = SimpleCache()


def register_blueprints(app):
    # Prevents circular imports
    from views import static_page
    from views import search_scripts
    from views import others
    from views import blog
    #from views import admin
    app.register_blueprint(static_page)
    app.register_blueprint(search_scripts)
    app.register_blueprint(others)
    app.register_blueprint(blog)

register_blueprints(app)


@app.route('/register/', methods=["GET", "POST"])
def register_page():
    try:
        form = RegistrationForm(request.form)
        if request.method == "POST" and form.validate():
            username = form.username.data
            email = form.email.data
            password = sha256_crypt.encrypt((str(form.password.data)))
            c, conn = connection()

            x = c.execute(
                "SELECT * FROM users WHERE username = '{0}'".format(thwart(username)))

            if int(x) > 0:
                flash("That username is already taken, please choose another")
                return render_template('register.html', form=form)

            else:
                c.execute("INSERT INTO users (username, password, email) VALUES ('{0}', '{1}', '{2}')"
                          .format(thwart(username), thwart(password), thwart(email)))

                conn.commit()
                flash("Thanks for registering!")
                c.close()
                conn.close()
                gc.collect()

                session['logged_in'] = True
                session['username'] = username

                return redirect(url_for('blog.homepage'))

        return render_template("register.html", form=form)

    except Exception as e:
        return(str(e))


@app.route('/login/', methods=['GET', 'POST'])
def login():
    error = ''
    try:
        c, conn = connection()
        if request.method == "POST":
            data = c.execute("SELECT * FROM users WHERE username = '{0}';"
                             .format(thwart(request.form['username'])))  # username from database

            data = c.fetchone()[2]  # password

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
        gc.collect()
        return redirect(url_for('blog.homepage'))

    except Exception as e:
        error = "Invalid credentials, try again"
        flash(error)
        return redirect(url_for('blog.homepage'))
        # flash("Invalid credentials, try again")
        # return redirect(url_for('blog.homepage'))


@app.route("/logout/")
@login_required
def logout():
    session.clear()
    flash("You have been logged out")
    gc.collect
    return redirect(url_for('blog.homepage'))


# Search_Scripts Function
@app.route('/send-mail/')
def send_mail():
    try:
        msg = Message("Send Mail Tutorial!",
                      sender="frankchi24@gmail.com",
                      recipients=["frankchi25@gmail.com"])
        msg.body = "So you wanna receive the new email!!"
        mail.send(msg)
        flash('Mail Sent')
        return redirect(url_for('blog.homepage'))
    except Exception, e:
        return(str(e))


if __name__ == "__main__":
    app.debug = True
    app.run()
    # to avoid runtime error
