from flask import Flask, render_template
from content_management import Content

TOPIC_DIC = Content()

app = Flask(__name__)

@app.route('/')
def homepage():
    return render_template("main.html",TOPIC_DIC = TOPIC_DIC)

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


app.config.update(
    PROPAGATE_EXCEPTIONS = True
)

if __name__ == "__main__":
    app.run()