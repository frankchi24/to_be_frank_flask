# -*- coding: utf-8 -*-
from flask import Flask, request, session, g, redirect, url_for, Blueprint, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from FlaskApp.forms import RegistrationForm, post_submit
from FlaskApp.models import posts, scripts, db
from FlaskApp.util import admin_required, login_required
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
        title_list = posts.query.paginate(page, 5, False).items
        pagination_list = posts.query.paginate(page, 5, False)

        return render_template("blog_archive.html", title_list=title_list, page=page, pagination_list=pagination_list)
    except Exception, e:
        return('blog_archive page error: ' + str(e))


@blog.route('/admin_panel/')
@blog.route('/admin_panel/page/<int:page>/')
def admin_panel(page=1):
    try:
        title_list = posts.query.paginate(page, 5, False).items
        pagination_list = posts.query.paginate(page, 5, False)
        return render_template("admin_panel.html", title_list=title_list, page=page, pagination_list=pagination_list)
    except Exception, e:
        return('admin_panel page error: ' + str(e))


@blog.route('/delete/<int:pid>/')
@login_required
@admin_required
def delete(pid):
    # delete
    post = posts.query.filter_by(id=pid)
    post_title = post.first().title
    post.delete()
    db.session.commit()
    flash('The post [%s] is deleted' % (post_title))
    return redirect(url_for('blog.admin_panel'))


@blog.route('/new_post/', methods=['GET', 'POST'])
@login_required
@admin_required
def new_post():
    form = post_submit(request.form)
    if request.method == "POST" and form.validate():
        title = form.title.data
        sub_title = form.sub_title.data
        author = form.author.data
        date_time = form.date.data
        page_down = form.pagedown.data
        post_content = markdown(form.pagedown.data)
        hold_post = posts(title, sub_title, author,
                          date_time, post_content, page_down)
        db.session.add(hold_post)
        db.session.commit()
        flash("Thanks for posting!")
        return redirect(url_for('blog.post', post_name=title))
    else:
        pass
    return render_template("panel.html", form=form)


@blog.route('/edit/<int:pid>/', methods=['GET', 'POST'])
@login_required
@admin_required
def editor(pid):
    try:
        post = posts.query.filter_by(id=pid).first()
        form = post_submit(request.form,
                           title=post.title,
                           sub_title=post.sub_title,
                           author=post.author,
                           date=post.date_time,
                           pagedown=post.page_down)
        if request.method == "POST" and form.validate():
            post.title = form.title.data
            new_title = post.title
            post.sub_title = form.sub_title.data
            post.author = form.author.data
            post.date_time = form.date.data
            post.post_content = markdown(form.pagedown.data)
            post.page_down = form.pagedown.data
            db.session.commit()
            flash(post.page_down)
            return redirect(url_for('blog.post', post_name=new_title))
        else:
            pass
        return render_template("panel.html", form=form)
    except Exception as e:
        return('editor page error: ' + str(e))
