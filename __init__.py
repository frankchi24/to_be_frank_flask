# -*- coding: utf-8 -*-
from flask import Flask, render_template, flash, session, request, url_for, redirect, send_file, send_from_directory, jsonify
from dbconnect import connection, connection_scripts
from wtforms import Form, BooleanField, StringField, PasswordField, validators, DateField, TextAreaField, SubmitField
from passlib.hash import sha256_crypt
from MySQLdb import escape_string as thwart
import gc
from functools import wraps
from wtforms.fields.html5 import DateField
from flask_mail import Mail, Message
import smtplib
import os
import pygal
from flask_misaka import markdown
from flask_pagedown import PageDown
from flask_pagedown.fields import PageDownField
from tempfile import mkstemp
# from flask_cache import Cache
# from werkzeug.contrib.cache import SimpleCache
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, and_, or_, asc, desc
from sqlalchemy.sql import select

app = Flask(
    __name__, instance_path='/Users/Mac/Downloads/Coding/flask/FlaskApp/FlaskApp/protected')
app.secret_key = "frankchi24"

# MAIL
app.config.update(
    DEBUG=True,
    # EMAIL SETTINGS
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME='frankchi24@gmail.com',
    MAIL_PASSWORD='ppzc jgyf ihrx dbov',
    SQLALCHEMY_DATABASE_URI='mysql+mysqldb://root:bestdrumer322@localhost/to_be_frank?charset=utf8',
    SQLALCHEMY_NATIVE_UNICODE=True,
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)
mail = Mail(app)
pagedown = PageDown(app)

# cache = Cache(app, config={'CACHE_TYPE': 'simple'})
# cache = SimpleCache()

# SQLAlchemy
db = SQLAlchemy(app)
# Base = automap_base()
# db.reflect()  # reflection to get table meta


class scripts(db.Model):
    sid = db.Column(db.Integer, primary_key=True)
    scripts = db.Column(db.String(500), unique=False)
    position = db.Column(db.String(11), unique=False)
    time_stamp = db.Column(db.String(100), unique=False)
    epinumber = db.Column(db.Integer(), unique=False)
    season = db.Column(db.Integer(), unique=False)
    show_name = db.Column(db.String(100), unique=False)
    footnote = db.Column(db.BLOB(), unique=False)
    tags = db.Column(db.String(100), unique=False)

    def __init__(self, sid, scripts, position, time_stamp, epinumber, season, show_name, footnote, tags):
        self.sid = sid
        self.scripts = scripts
        self.position = position
        self.time_stamp = time_stamp
        self.epinumber = epinumber
        self.season = season
        self.show_name = show_name
        self.season = season
        self.footnote = footnote
        self.tagss = tags

    def __repr__(self):
        return '<scripts %r>' % self.scripts


class posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True)
    sub_title = db.Column(db.String(120), unique=False)
    author = db.Column(db.String(20), unique=False)
    date_time = db.Column(db.Date(), unique=False)
    post_content = db.Column(db.Text(), unique=False)

    def __init__(self, title, sub_title, author, date_time, post_content):
        self.title = title
        self.sub_title = sub_title
        self.author = author
        self.date_time = date_time
        self.post_content = post_content

    def __repr__(self):
        return '<posts %r>' % self.title

db.create_all()


class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=20)])
    email = StringField('Email Address', [validators.Length(min=6, max=50)])
    password = PasswordField('New Password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField(
        'I accept the Terms of Service and Privacy Notice (updated Jan 22, 2015)', [validators.Required()])


class post_submit(Form):
    title = StringField(
        'Title', [validators.Required(), validators.Length(min=1, max=20)])
    sub_title = StringField('Subtitle')
    author = StringField('Author', [validators.Length(min=1, max=20)])
    date = DateField('date', format='%Y-%m-%d')
    pagedown = PageDownField('Enter your markdown')


class search(Form):
    title = StringField('title', [validators.Length(min=3, max=20)])


def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'admin' == session['username']:
            return f(*args, **kwargs)
        else:
            flash("You are not admin")
            return redirect(url_for('homepage'))
    return wrap


def get_list_of_shows():
    c, conn = connection_scripts()
    list_of_show = []
    c.execute("SELECT DISTINCT show_name FROM scripts;")
    for show in c:
        list_of_show.append(show)
    c.close()
    conn.close()
    return list_of_show


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('login'))
    return wrap


def search_scripts_sqlalchemy(page, select, title):
    title1 = '%' + title + '%'
    title2 = '%' + title + ' %'
    if select == "all":
        rows = scripts.query.filter(or_(scripts.scripts.like(
            title1), scripts.scripts.like(title2))).paginate(page, 25, False)

    else:
        rows = scripts.query.filter(and_(scripts.show_name == select,
                                         or_(scripts.scripts.like(title1),
                                             scripts.scripts.like(title2))
                                         )
                                    ).paginate(page, 30, False)
    for row in rows.items:
        context1 = scripts.query.filter(
            scripts.sid < row.sid).order_by(desc(scripts.sid)).limit(2).all()
        context2 = scripts.query.filter(
            scripts.sid >= row.sid).order_by(asc(scripts.sid)).limit(2).all()
        context = context1 + context2
        test = ''
        for c in context:
            test = test + c.scripts
        row.footnote = test
    return rows


def header_image_path(title):
    path = {"How I Met Your Mother": 'img/tv_show_background.jpg',
            "House of Cards": 'img/tv_show_background.jpg',
            "Suits": 'img/tv_show_background.jpg',
            "Mad Men": 'img/tv_show_background.jpg', "The Big Bang Theory": 'img/tv_show_background.jpg',
            }
    search_header_path = path[title]
    return search_header_path


@app.route('/')
def homepage():
    try:
        form = RegistrationForm(request.form)
        title_list = posts.query.limit(3).all()

        return render_template("main.html", title_list=title_list)
    except Exception as e:
        return 'main page error: ' + str(e)


@app.route('/blog_archive/')
@app.route('/blog_archive/page/<int:page>/')
def blog_archive(page=1):
    try:
        title_list = posts.query.paginate(page, 3, False).items
        pagination_list = posts.query.paginate(page, 3, False)
        return render_template("blog_archive.html", title_list=title_list, page=page, pagination_list=pagination_list)
    except Exception, e:
        return('blog_archive page error: ' + str(e))


@app.route('/post/<string:post_name>/')
def post(post_name):
    try:
        row = posts.query.filter_by(title=post_name).first()
        title = row.title
        sub_title = row.sub_title
        author = row.author
        date_time = row.date_time
        post = row.post_content
        return render_template("post.html",
                               title=title,
                               sub_title=sub_title,
                               author=author,
                               date_time=date_time,
                               post=post)
    except Exception, e:
        return('post page error: ' + str(e))


@app.route('/about/')
def about():
    return render_template("about.html")


@app.route('/panel/', methods=['GET', 'POST'])
@login_required
@admin_required
def panel():
    try:
        form = post_submit(request.form)
        if request.method == "POST":
            title = form.title.data
            sub_title = form.sub_title.data
            author = form.author.data
            date_time = form.date.data
            post_content = markdown(form.pagedown.data)
            hold_post = posts(title, sub_title, author,
                              date_time, post_content)
            db.session.add(hold_post)
            db.session.commit()
            flash("Thanks for posting!")
            return redirect(url_for('post', post_name=title))
        else:
            return render_template("panel.html", form=form)
    except Exception as e:
        return('Panel page error: ' + str(e))
    return render_template("panel.html")


@app.route('/contact/')
def contact():
    return render_template("contact.html")


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

                return redirect(url_for('homepage'))

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

                return redirect(url_for('homepage'))
            else:
                error = "Invalid credentials, try again"
                flash(error)
        gc.collect()
        return redirect(url_for('homepage'))

    except Exception as e:
        error = "Invalid credentials, try again"
        flash(error)
        return redirect(url_for('homepage'))
        # flash("Invalid credentials, try again")
        # return redirect(url_for('homepage'))


@app.route("/logout/")
@login_required
def logout():
    session.clear()
    flash("You have been logged out")
    gc.collect
    return redirect(url_for('homepage'))


# Search_Scripts Function


@app.route('/scripts_search/', methods=['GET', 'POST'])
@login_required
@admin_required
def scripts_search():
    try:
        form = search(request.form)
        list_of_show = get_list_of_shows()

        # get the list of all shows in databases
        if request.method == "POST" and form.validate():
            title = form.title.data.encode('utf8')
            select = request.form.get('select_show').encode('utf8')
            return redirect(url_for('search_results', title=title, select=select, page=1))
        else:
            return render_template("scripts_search.html", form=form, list_of_show=list_of_show)

    except Exception as e:
        flash(e)
        return('Scripts search page error: ' + str(e))
        # error page


@app.route("/search_results/<string:select>/<string:title>/<int:page>/", methods=['GET', 'POST'])
@login_required
@admin_required
def search_results(select, title, page):
    try:
        form = search(request.form)
        list_of_show = get_list_of_shows()
        if request.method == "POST" and form.validate():
            title = form.title.data
            select = request.form.get('select_show')
            return redirect(url_for('search_results', title=title, select=select))

        title = title.encode('utf-8')
        select = select.encode('utf-8')
        pagination = search_scripts_sqlalchemy(page, select, title)
        flash(pagination.pages)
        result_list = pagination.items
        return render_template("search_results.html",
                               result_list=result_list,
                               pagination=pagination,
                               page=page,
                               form=form,
                               list_of_show=list_of_show,
                               title=title,
                               select=select)
    except Exception as e:
        return('Search result page error: ' + str(e))
        # flash("Sorry, can't find any match.")
        # return render_template("scripts_search.html", form=form,
        #                        list_of_show=list_of_show)


@app.route("/file_downloads/")
def file_downloads():
    try:
        pass
        # get variables title
        # print stuff in the text file
        # get return file downd
    except Exception as e:
        return ('File download page error: ' + str(e))
        # return render_template("downloads.html")


# file handling


@app.route("/return_files/")
def return_files():
    os_path = '/Users/Mac/Downloads/Coding/flask/FlaskApp/FlaskApp/protected/'

    return send_file(os_path, as_attachment=True)


@app.route('/send-mail/')
def send_mail():
    try:
        msg = Message("Send Mail Tutorial!",
                      sender="frankchi24@gmail.com",
                      recipients=["frankchi25@gmail.com"])
        msg.body = "So you wanna receive the new email!!"
        mail.send(msg)
        flash('Mail Sent')
        return redirect(url_for('homepage'))
    except Exception, e:
        return(str(e))


@app.route('/protected/<path:filename>')
@login_required
@admin_required
def protected(filename):
    try:
        return send_from_directory(
            os.path.join(app.instance_path, ''),
            filename
        )
    except:
        return redirect(url_for('homepage'))


# jquery
@app.route('/interactive/')
def interactive():
    return render_template('interactive.html')


@app.route('/background_process')
def background_process():
    try:
        lang = request.args.get('proglang', 0, type=str)
        return jsonify(result=lang)
    except Exception as e:
        return str(e)


# pygal
@app.route('/pygalexample/')
def pygalexample():
    try:
        graph = pygal.Pie()
        graph.title = '% Change Coolness of programming languages over time.'
        graph.x_labels = ['2011', '2012', '2013', '2014', '2015', '2016']
        graph.add('Python',  [15, 31, 89, 200, 356, 900])
        graph.add('Java',    [15, 45, 76, 80,  91,  95])
        graph.add('C++',     [5,  51, 54, 102, 150, 201])
        graph.add('All others combined!',  [5, 15, 21, 55, 92, 105])
        graph_data = graph.render_data_uri()
        return render_template("graphing.html", graph_data=graph_data)
    except Exception as e:
        return str(e)


@app.errorhandler(405)
def method_not_found(e):
    return render_template('/405.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('/404.html')


app.config.update(
    PROPAGATE_EXCEPTIONS=True
)

if __name__ == "__main__":
    app.debug = True
    app.run()
    # to avoid runtime error
