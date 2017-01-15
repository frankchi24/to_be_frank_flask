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
    footnote = db.Column(db.String(1000), unique=False)
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


def search_scripts_database(select, title):
    c, conn = connection_scripts()
    if select == "all":
        c.execute("SELECT scripts, season, epinumber, position, time_stamp, show_name, sid FROM scripts WHERE scripts LIKE '%{1} %' OR scripts LIKE '%{2},%' OR scripts LIKE '%{3}.%' OR scripts LIKE '%{4}?%' LIMIT 100".format(
            select, thwart(title), thwart(title), thwart(title), thwart(title), thwart(title)))
    else:
        c.execute("SELECT scripts, season, epinumber, position, time_stamp, show_name, sid FROM scripts WHERE show_name = '{0}' AND (scripts LIKE '%{1} %' OR scripts LIKE '%{2},%' OR scripts LIKE '%{3}.%' OR scripts LIKE '%{4}?%') LIMIT 100".format(
            select, thwart(title), thwart(title), thwart(title), thwart(title), thwart(title)))
    result_list = []
    for row in c:
        try:
            scripts_decode = row[0].decode('utf-8')
        except UnicodeDecodeError:
            scripts_decode = row[0].decode('latin-1')
            # handle some substring using latin-1 decoding
        result_list.append({"scripts": scripts_decode,
                            "season": row[1],
                            "epinumber": row[2],
                            "position": row[3],
                            "time_stamp": row[4],
                            "show_name": row[5].decode('utf-8'),
                            "sid": row[6]}
                           )
    # put search result into a list of dictionaries
        for item in result_list:
            context_result_list = []
            sid = item["sid"]
            c.execute("""(SELECT position,time_stamp, scripts, sid FROM scripts WHERE sid < '{0}' ORDER BY sid DESC LIMIT 2)UNION(SELECT position,time_stamp, scripts, sid FROM scripts WHERE sid >= '{1}' ORDER BY sid ASC LIMIT 2)ORDER BY position ASC;""".format(
                sid, sid))
            for new_row in c:
                test_dic = {}
                test_dic["position"] = new_row[0]
                test_dic["time_stamp"] = new_row[1]
                test_dic["scripts"] = []
                try:
                    context_scripts_decode = new_row[2].decode('utf-8')
                except UnicodeDecodeError:
                    context_scripts_decode = new_row[2].decode('latin-1')
                # handle some substring using latin-1 decoding
                test_dic["scripts"].append(context_scripts_decode)
                test_dic["sid"] = new_row[3]
                context_result_list.append(test_dic)
            item["context"] = context_result_list
            # for each of the search result, get 4 lines of context and add as
            # the last dic in result_list
    c.close()
    conn.close()
    gc.collect()
    return result_list


def search_scripts_sqlalchemy(select, title):
    result_list = []
    title = '%' + title + ' %'
    title2 = '%' + title + ' %'
    if select == "all":
        rows = scripts.query.filter(or_(scripts.scripts.like(
            title), scripts.scripts.like(title2))).limit(1000).all()
    else:
        rows = scripts.query.filter(
            and_(
                scripts.show_name == select,
                or_(scripts.scripts.like(title), scripts.scripts.like(title2))
            )
        ).limit(1000).all()
    for row in rows:
        context1 = scripts.query.filter(scripts.sid < row.sid).order_by(
            desc(scripts.sid)).limit(3).all()
        context2 = scripts.query.filter(
            scripts.sid >= row.sid).order_by(asc(scripts.sid)).limit(3).all()
        context_list = context1 + context2
        result_list.append({"scripts": row.scripts,
                            "season": row.season,
                            "epinumber": row.epinumber,
                            "position": row.position,
                            "time_stamp": row.time_stamp,
                            "show_name": row.show_name,
                            "sid": row.sid,
                            "context": context_list
                            })
    return result_list


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
        title_list = []
        for row in posts.query.all():
            title_list.append({"title": row.title,
                               "sub_title": row.sub_title,
                               "author": row.author,
                               "date_time": row.date_time})
        return render_template("main.html", title_list=title_list)
    except Exception as e:
        return 'main page error: ' + str(e)
        # c, conn = connection()
        # c.execute(
        #     "SELECT pid, title, sub_title , author, date_time FROM posts ORDER BY date_time ASC LIMIT 3 ;")
        # for row in c:
        #     title_list.append({"title": row[1].decode('utf8'),
        #                        "sub_title": row[2].decode('utf8'),
        #                        "author": row[3].decode('utf8'),
        #                        "date_time": row[4]})
        # conn.commit()
        # c.close()
        # conn.close()
        # gc.collect()


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
    # using sql approach
    # c, conn = connection()
    # c.execute("INSERT INTO posts (title, sub_title, author, date_time, post) VALUES ('{0}', '{1}', '{2}', '{3}','{4}');".format(
    #     title, sub_title, author, date, post_content))
    # conn.commit()
    # flash("Thanks for posting!")
    # c.close()
    # conn.close()
    # gc.collect()


@app.route('/contact/')
def contact():
    return render_template("contact.html")


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


@app.route('/blog_archive/')
def blog_archive():
    try:
        title_list = []
        c, conn = connection()
        c.execute(
            "SELECT pid, title, sub_title , author, date_time FROM posts ORDER BY date_time ASC;")
        for row in c:
            title_list.append({"title": row[1].decode('utf-8'),
                               "sub_title": row[2].decode('utf-8'),
                               "author": row[3].decode('utf-8'),
                               "date_time": row[4]}
                              )
        conn.commit()
        c.close()
        conn.close()
        gc.collect()
        return render_template("blog_archive.html", title_list=title_list)
    except Exception, e:
        return('All_posts page error: ' + str(e))


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
            title = form.title.data
            select = request.form.get('select_show')
            return redirect(url_for('search_results', title=title, select=select))
        else:
            return render_template("scripts_search.html", form=form, list_of_show=list_of_show)

    except Exception as e:
        flash(e)
        return('Scripts search page error: ' + str(e))
        # error page


@app.route("/search_results/<string:select>/<string:title>", methods=['GET', 'POST'])
@login_required
@admin_required
def search_results(select, title):
    try:
        form = search(request.form)
        list_of_show = get_list_of_shows()
        if request.method == "POST" and form.validate():
            title = form.title.data
            select = request.form.get('select_show')
            return redirect(url_for('search_results', title=title, select=select))

        title = title.encode('utf-8')
        select = select.encode('utf-8')
        # result_list = search_scripts_database(select, title)
        result_list = search_scripts_sqlalchemy(select, title)
        result_count = len(result_list)
        return render_template("search_results.html",
                               result_list=result_list,
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
