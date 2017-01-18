from flask import Flask, request, session, g, redirect, url_for, Blueprint, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from forms import RegistrationForm, post_submit
from FlaskApp.models import posts, scripts, db
from util import admin_required, login_required
from flask_misaka import markdown

blog = Blueprint('blog', __name__)


@blog.route('/')
def homepage():
    try:
        form = RegistrationForm(request.form)
        title_list = posts.query.limit(3).all()
        return render_template("main.html", title_list=title_list)
    except Exception as e:
        return 'main page error: ' + str(e)


@blog.route('/post/<string:post_name>/')
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


@blog.route('/blog_archive/')
@blog.route('/blog_archive/page/<int:page>/')
def blog_archive(page=1):
    try:
        title_list = posts.query.paginate(page, 3, False).items
        pagination_list = posts.query.paginate(page, 3, False)
        return render_template("blog_archive.html", title_list=title_list, page=page, pagination_list=pagination_list)
    except Exception, e:
        return('blog_archive page error: ' + str(e))


@blog.route('/panel/', methods=['GET', 'POST'])
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
            return redirect(url_for('blog.post', post_name=title))
        else:
            return render_template("panel.html", form=form)
    except Exception as e:
        return('Panel page error: ' + str(e))
    return render_template("panel.html")
