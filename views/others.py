# -*- coding: utf-8 -*-
from flask import Flask, request, session, g, redirect, url_for, Blueprint, flash, render_template, jsonify, send_file, send_from_directory
from util import admin_required, login_required
import smtplib
import os
import pygal
from FlaskApp import app


others = Blueprint('others', __name__)


# jquery
@others.route('/interactive/')
def interactive():
    return render_template('interactive.html')


@others.route('/background_process/')
def background_process():
    try:
        lang = request.args.get('proglang', 0, type=str)
        return jsonify(result=lang)
    except Exception as e:
        return str(e)

 # download files


@others.route("/return_files/")
def return_files():
    os_path = '/Users/Mac/Downloads/Coding/flask/FlaskApp/FlaskApp/protected/test.pdf'
    return send_file(os_path, as_attachment=True)


@others.route('/protected/<path:filename>/')
@login_required
@admin_required
def protected(filename):
    try:
        return send_from_directory(
            os.path.join(app.instance_path, ''),
            filename
        )
    except Exception as e:
        flash(str(e))
        return redirect(url_for('blog.homepage'))

# pygal


@others.route('/pygalexample/')
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


@others.errorhandler(405)
def method_not_found(e):
    return render_template('/405.html')


@others.errorhandler(404)
def page_not_found(e):
    return render_template('/404.html')
