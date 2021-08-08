from flask import render_template
from app import app
from app.forms import LoginForm


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")


@app.route("/login")
def login():
    return render_template("login.html", form=LoginForm())
