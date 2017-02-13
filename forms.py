from wtforms import Form, BooleanField, StringField, PasswordField, validators, DateField, TextAreaField, SubmitField, TextField
from wtforms.fields.html5 import DateField
from flask_misaka import markdown
from flask_pagedown import PageDown
from flask_pagedown.fields import PageDownField


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
    tags = StringField('tags', [validators.Length(max=200)])
    author = StringField('Author', [validators.Length(min=1, max=20)])
    date = DateField('Date', format='%Y-%m-%d')
    pagedown = PageDownField('Enter your markdown')

class new_tag(Form):
    tags = StringField('new_tag', [validators.Length(min=3, max=20)])

class search(Form):
    title = StringField('title', [validators.Length(min=3, max=20)])
