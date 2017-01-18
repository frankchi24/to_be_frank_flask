# -*- coding: utf-8 -*-
from flask import Flask, request, session, g, redirect, url_for, Blueprint, flash, render_template
from FlaskApp.util import admin_required, login_required
from FlaskApp.forms import *
from FlaskApp.models import get_list_of_shows, search_scripts_sqlalchemy, header_image_path

search_scripts = Blueprint('search_scripts', __name__)


@search_scripts.route('/scripts_search/', methods=['GET', 'POST'])
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
            return redirect(url_for('search_scripts.search_results', title=title, select=select, page=1))
        else:
            return render_template("scripts_search.html", form=form, list_of_show=list_of_show)

    except Exception as e:
        flash(e)
        return('Scripts search page error: ' + str(e))
        # error page


@search_scripts.route("/search_results/<string:select>/<string:title>/<int:page>/", methods=['GET', 'POST'])
@login_required
@admin_required
def search_results(select, title, page):
    try:
        form = search(request.form)
        list_of_show = get_list_of_shows()
        if request.method == "POST" and form.validate():
            title = form.title.data
            select = request.form.get('select_show')
            return redirect(url_for('search_scripts.search_results', title=title, select=select))

        title = title.encode('utf-8')
        select = select.encode('utf-8')
        pagination = search_scripts_sqlalchemy(page, select, title)
        flash(pagination.pages)
        result_list = pagination.items
        header_image = header_image_path(select)
        return render_template("search_results.html",
                               result_list=result_list,
                               pagination=pagination,
                               page=page,
                               form=form,
                               header_image=header_image,
                               list_of_show=list_of_show,
                               title=title,
                               select=select)
    except Exception as e:
        return('Search result page error: ' + str(e))
        # flash("Sorry, can't find any match.")
        # return render_template("scripts_search.html", form=form,
        #                        list_of_show=list_of_show)
