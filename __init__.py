from flask import Flask, render_template, flash, session 
from content_management import Content

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



@app.errorhandler(404)
def page_not_found(e):
	return render_template('/404.html')


app.config.update(
    PROPAGATE_EXCEPTIONS = True
)

if __name__ == "__main__":
	app.debug = True 
	app.run()
	# to avoid runtime error
  