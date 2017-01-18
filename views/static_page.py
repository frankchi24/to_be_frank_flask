# -*- coding: utf-8 -*-
from flask import Flask, request, session, g, redirect, url_for, Blueprint, flash, render_template
from util import admin_required, login_required

static_page = Blueprint('static_page', __name__)


@static_page.route('/about/')
def about():
    return render_template("about.html")


@static_page.route('/contact/')
def contact():
    return render_template("contact.html")
