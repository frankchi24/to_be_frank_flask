# -*- coding: utf-8 -*-
from flask import Flask, request, session, g, redirect, url_for, Blueprint, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from FlaskApp.forms import RegistrationForm, post_submit,new_tag
from FlaskApp.models import posts, scripts, tag,users, db
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
        post = posts.query.filter_by(title=post_name).first()
        return render_template("post.html",post = post)
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


@blog.route('/tag/')
@blog.route('/tag/<string:select_tag>/')
def posts_for_tag(select_tag):
    try:
        select = tag.query.filter_by(tag_name = select_tag).first()
        title_list = select.posts
        return render_template("tag_post.html", title_list=title_list, select_tag= select_tag)
    except Exception, e:
        flash('No tag as ' + select_tag)
        return redirect(url_for('blog.blog_archive'))

@blog.route('/author/')
@blog.route('/author/<string:author>/')
def author_for_post(author):
    try:
        user = users.query.filter_by(username = author).first()
        select_author = posts.query.filter_by(user_id = user.uid).all()
        title_list = select_author
        return render_template("author_post.html", title_list=title_list, author= author)
    except Exception, e:
        flash(" No result for author " + author)
        return redirect(url_for('blog.blog_archive'))


@blog.route('/admin_panel/', methods=['GET', 'POST'])
@blog.route('/admin_panel/page/<int:page>/')
def admin_panel(page=1):
    try:
        form = new_tag(request.form)
        if request.method == "POST" and form.validate():
            db.session.add(tag(form.tags.data))
            db.session.commit()
            flash("\"%s\" has been successfully added" % (form.tags.data))
            return redirect(url_for('blog.admin_panel'))

        tags = tag.query.all()
        title_list = posts.query.paginate(page, 5, False).items
        pagination_list = posts.query.paginate(page, 5, False)
        return render_template("admin_panel.html", title_list=title_list, page=page, pagination_list=pagination_list, form = form, tags = tags)
    except Exception, e:
        return('admin_panel page error: ' + str(e))


@blog.route('/delete/<int:pid>/')
@login_required
@admin_required
def delete(pid):
    # delete
    post = posts.query.filter_by(id=pid)
    post_title = post.first().title
    post.first().tags = []
    #get rid of the relationship
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
        date_time = form.date.data
        page_down = form.pagedown.data
        tag_string = form.tags.data
        post_content = markdown(form.pagedown.data)
        user = users.query.filter_by(username= session['username']).first()
        user_id  = user.uid
        
        hold_post = posts(title, sub_title, session['username'],
                          date_time,post_content, page_down,user_id)
        hold_post._set_tags(tag_string)
        db.session.add(hold_post)
        db.session.commit()
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
        tag_string = ''
        for tag in post._get_tags():
            tag_string = tag_string + tag.tag_name + ','

        form = post_submit(request.form,
                           title=post.title,
                           sub_title=post.sub_title,
                           date=post.date_time,
                           tags=tag_string,
                           pagedown=post.page_down)
        if request.method == "POST" and form.validate():
            post.title = form.title.data
            new_title = post.title
            post.sub_title = form.sub_title.data
            post.date_time = form.date.data
            post._set_tags(form.tags.data)
            post.post_content = markdown(form.pagedown.data)
            post.page_down = form.pagedown.data
            db.session.commit()
            return redirect(url_for('blog.post', post_name=new_title))
        else:
            pass
        return render_template("panel.html", form=form)
    except Exception as e:
        return('editor page error: ' + str(e))
