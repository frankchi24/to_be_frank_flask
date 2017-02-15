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
    instance_path='/Users/Frank/Dropbox/Coding/Flask/flask/FlaskApp/instance')
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
    from views import signin_view
    #from views import admin
    app.register_blueprint(static_page)
    app.register_blueprint(search_scripts)
    app.register_blueprint(others)
    app.register_blueprint(blog)
    app.register_blueprint(signin_view)

register_blueprints(app)




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

