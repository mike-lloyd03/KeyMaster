from flask import render_template, flash, redirect, url_for
from app import app, db

from app.forms import LoginForm, NewKeyForm
from app.models import Key


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html", form=LoginForm())


@app.route("/keys")
def keys():
    keys = Key.query.all()
    return render_template("keys.html", keys=keys)


@app.route("/add_key", methods=["GET", "POST"])
def add_key():
    form = NewKeyForm()
    if form.validate_on_submit():
        key = Key(name=form.name.data, description=form.description.data)
        db.session.add(key)
        db.session.commit()
        flash("Key added")
        return redirect(url_for("keys"))
    return render_template("new_key.html", form=NewKeyForm())
