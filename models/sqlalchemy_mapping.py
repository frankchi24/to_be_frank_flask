# -*- coding: utf-8 -*-
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.sql import select
from FlaskApp import app

# SQLAlchemy
# Base = automap_base()
# db.reflect()  # reflection to get table meta

db = SQLAlchemy(app)


class posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True)
    sub_title = db.Column(db.String(120), unique=False)
    author = db.Column(db.String(20), unique=False)
    date_time = db.Column(db.Date(), unique=False)
    post_content = db.Column(db.Text(), unique=False)
    page_down = db.Column(db.Text(), unique=False)

    def __init__(self, title, sub_title, author, date_time, post_content, page_down):
        self.title = title
        self.sub_title = sub_title
        self.author = author
        self.date_time = date_time
        self.post_content = post_content
        self.page_down = page_down

    def __repr__(self):
        return '<posts %r>' % self.title


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

db.create_all()
