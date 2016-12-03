# -*- coding: utf-8 -*-
from flask import Flask, render_template, flash, session,request,url_for,redirect
from content_management import Content
from dbconnect import connection
from wtforms import Form

TOPIC_DIC = Content()

app = Flask(__name__)
app.secret_key = "frankchi24"

@app.route('/')
def homepage():
	return render_template("main.html",TOPIC_DIC = TOPIC_DIC)	
	
	# another way to show error
	# try:
	# 	return render_template("main.html",TOPIC_DIC = TOPIC_DI)	
	
	# except Exception as e:
	# 	return str(e)
@app.route('/about/')
def about():
	return render_template("/about.html")

@app.route('/project/')
def project():
    return render_template("/project.html")

@app.route('/contact/')
def contact():
	return render_template("/contact.html")

@app.route('/post/')
def post():
    return render_template("/post.html")




class RegistrationForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=20)])
    email = TextField('Email Address', [validators.Length(min=6, max=50)])
    password = PasswordField('New Password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the Terms of Service and Privacy Notice (updated Jan 22, 2015)', [validators.Required()])


@app.route('/register/', methods = ['GET','POST'])
def register_page():
	try:
		c, conn = connection()
		return("okay")
	except Exception as e:
		return(str(e))

@app.route('/login/', methods = ['GET','POST'])
def login():
	error = ''
	try:
		if request.method == "POST":
			attempted_username = request.form['username']
			attempted_password = request.form['password']

			# flash(attempted_username)
			# flash(attempted_password)

			if attempted_username == "admin" and attempted_password == "password":
				return redirect (url_for('post'))
			else:
				error = "Invalid, Try Again"
		
		return render_template("login.html", error = error)
	except Exception as e:
		return render_template("login.html", error = error)
		
@app.errorhandler(404)
def page_not_found(e):
	return render_template('/404.html')

@app.errorhandler(405)
def method_not_found(e):
	return render_template('/405.html')


app.config.update(
    PROPAGATE_EXCEPTIONS = True
)

if __name__ == "__main__":
	app.debug = True 
	app.run()
	# to avoid runtime error
  