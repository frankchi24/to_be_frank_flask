# -*- coding: utf-8 -*-
from flask import Flask, render_template, flash, session, request, url_for, redirect
from dbconnect import connection
from wtforms import Form, BooleanField, TextField, PasswordField, validators, DateField, TextAreaField
from passlib.hash import sha256_crypt
from MySQLdb import escape_string as thwart
import gc
from functools import wraps
from wtforms.fields.html5 import DateField


class RegistrationForm(Form):  # form class from wtfform
    username = TextField('Username', [validators.Length(min=4, max=20)])

    email = TextField('Email Address', [validators.Length(min=6, max=50)])

    password = PasswordField('New Password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])

    confirm = PasswordField('Repeat Password')

    accept_tos = BooleanField(
        'I accept the Terms of Service and Privacy Notice (updated Jan 22, 2015)', [
            validators.Required()
        ])


class post_submit(Form):
    title = TextField(
        'Title', [validators.Required(), validators.Length(min=4, max=20)])
    sub_title = TextField(
        'Subtitle', [validators.Required(), validators.Length(min=4, max=20)])
    author = TextField(
        'Author', [validators.Length(min=4, max=20)])
    date = DateField('date', format='%Y-%m-%d')

    post = TextAreaField(
        'Post')


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('login'))
    return wrap


app = Flask(__name__)
app.secret_key = "frankchi24"


@app.route('/')
def homepage():
    try:
        title_list = []
        c, conn = connection()
        c.execute(
            "SELECT pid, title, sub_title , author, date_time FROM posts ORDER BY date_time ASC LIMIT 3 ;")
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
        return render_template("main.html", title_list=title_list)

    except Exception as e:
        return 'main page error: ' + str(e)
    # another way to show error
    # try:
    # 	return render_template("main.html",TOPIC_DIC = TOPIC_DI)

    # except Exception as e:
    # 	return str(e)


@app.route('/about/')
def about():
    return render_template("about.html")


@app.route('/panel/', methods=['GET', 'POST'])
@login_required
def panel():
    try:
        form = post_submit(request.form)
        if request.method == "POST":
            title = form.title.data.encode('utf-8')
            sub_title = form.sub_title.data.encode('utf-8')
            author = form.author.data.encode('utf-8')
            date = form.date.data
            post = form.post.data.encode('utf-8')
            c, conn = connection()
            c.execute("INSERT INTO posts (title, sub_title, author, date_time, post) VALUES ('{0}', '{1}', '{2}', '{3}','{4}');".format(
                title, sub_title, author, date, conn.escape_string(str(post))))
            conn.commit()
            flash("Thanks for posting!")
            c.close()
            conn.close()
            gc.collect()
            return redirect(url_for('post', post_name=title.decode('utf-8')))
        else:
            return render_template("panel.html", form=form)
    except Exception as e:
        return('Panel page error: ' + str(e))
    return render_template("panel.html")


@app.route('/project/')
def project():
    return render_template("project.html")


@app.route('/contact/')
def contact():
    return render_template("contact.html")


@app.route('/post/<string:post_name>/')
def post(post_name):
    try:
        c, conn = connection()
        c.execute(
            "SELECT * FROM posts WHERE title = '{0}';".format(post_name.encode('utf-8')))
        for row in c:
            title = row[1].decode('utf-8')
            sub_title = row[2].decode('utf-8')
            author = row[3].decode('utf-8')
            date_time = row[4]
            post = row[5].decode('utf-8')
        conn.commit()
        c.close()
        conn.close()
        gc.collect()

        return render_template("post.html",
                               title=title,
                               sub_title=sub_title,
                               author=author,
                               date_time=date_time,
                               post=post)
    except Exception, e:
        return('post page error: ' + str(e))


@app.route('/all_posts/')
def all_posts():
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
        return render_template("all_posts.html", title_list=title_list)
    except Exception, e:
        return('All_posts page error: ' + str(e))


@app.route('/register/', methods=['GET', 'POST'])
def register_page():
    try:
        form = RegistrationForm(request.form)

        if request.method == "POST" and form.validate():
            username = form.username.data  # data would be what user typein
            email = form.email.data
            password = sha256_crypt.encrypt((str(form.password.data)))
            c, conn = connection()
            x = c.execute(
                "SELECT * FROM users WHERE username = '{0}';".format(thwart(username)))

            if int(x) > 0:
                flash("That username is already taken, please choose another")
                return render_template('register.html', form=form)
            else:
                c.execute("INSERT INTO users (username, password, email) VALUES ('{0}', '{1}', '{2}');".format(
                    thwart(username), thwart(password), thwart(email), thwart("/")))

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
        gc.collect()
        return render_template("login.html", error=error)

    except Exception as e:
        error = str(e)
        return render_template("login.html", error=error)


@app.route("/logout/")
@login_required
def logout():
    session.clear()
    flash("You have been logged out")
    gc.collect
    return redirect(url_for('homepage'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('/404.html')


@app.errorhandler(405)
def method_not_found(e):
    return render_template('/405.html')


app.config.update(
    PROPAGATE_EXCEPTIONS=True
)

if __name__ == "__main__":
    app.debug = True
    app.run()
    # to avoid runtime error
