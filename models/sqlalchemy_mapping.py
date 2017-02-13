# -*- coding: utf-8 -*-
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, DateTime
from FlaskApp import app
from datetime import datetime

# SQLAlchemy
# Base = automap_base()
# db.reflect()  # reflection to get table meta

db = SQLAlchemy(app)

tags = db.Table('tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'))
)


class posts(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True)
    sub_title = db.Column(db.String(120), unique=False)
    author = db.Column(db.String(20), unique=False)
    date_time = db.Column(db.Date(), unique=False)
    post_content = db.Column(db.Text(), unique=False)
    page_down = db.Column(db.Text(), unique=False)
    tags = db.relationship('tag', secondary=tags,
        backref=db.backref('posts', lazy='dynamic'))

    def __init__(self, title, sub_title, author, date_time, post_content, page_down):
        self.title = title
        self.sub_title = sub_title
        self.author = author
        self.date_time = date_time
        self.post_content = post_content
        self.page_down = page_down
        #shouldn't add tags here

    def _find_or_create_tag(self, string):
        q = tag.query.filter_by(tag_name=string)
        t = q.first()
        if not t:
            t = tag(string)
        return t

    def _get_tags(self):
        tag_list = []
        for tag in self.tags:
            tag_list.append(tag)
        return tag_list

    def _set_tags(self, string_given):
        # clear the list first
        while self.tags:
            del self.tags[0]

        # string to list
        list_given = string_given.split(',')
        # add new tag
        for t in list_given:
            self.tags.append(self._find_or_create_tag(t))

    def __repr__(self):
        return '<posts %r>' % self.title

class tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String(80), unique=True)

    def __init__(self, tag_name):
        self.tag_name = tag_name

    def __repr__(self):
        return '<tag %r>' % self.tag_name


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
