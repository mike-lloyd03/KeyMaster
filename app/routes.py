from flask import render_template, flash, redirect, url_for
from app import app, db

from app.forms import LoginForm, NewKeyForm, EditKeyForm, AssignKeyForm
from app.models import Key, User, Assignment

from datetime import datetime


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template("quick_form.html", form=LoginForm(), title="Login")


@app.route("/keys")
def keys():
    keys = Key.query.all()
    return render_template("keys.html", keys=keys)


@app.route("/add_key", methods=["GET", "POST"])
def add_key():
    form = NewKeyForm()
    if form.validate_on_submit():
        key = Key(name=form.name.data, description=form.description.data)
        key.add()
        flash(f'Key "{key.name}" added')
        return redirect(url_for("keys"))
    return render_template("quick_form.html", form=form, title="New Key")


@app.route("/edit_key", methods=["GET", "POST"])
def edit_key():
    form = EditKeyForm()
    if form.validate_on_submit():
        key = Key(name=form.name.data, description=form.description.data)
        key.add()
        flash(f'Key "{key.name}" added')
        return redirect(url_for("keys"))
    return render_template("quick_form.html", form=form, title="Edit Key")


@app.route("/assign_key", methods=["GET", "POST"])
def assign_key():
    users = User.query.all()
    keys = Key.query.all()
    form = AssignKeyForm()
    form.user.choices = [u.username for u in users]
    form.key.choices = [k.name for k in keys]
    if form.validate_on_submit():
        assignment = Assignment(
            user=form.user.data, key=form.key.data, date_out=form.date_out.data
        )
        db.session.add(assignment)
        db.session.commit()
        flash("Key assigned")
        return redirect(url_for("assignments"))
    return render_template("quick_form.html", form=form, title="Assign Key")


@app.route("/assignments", methods=["GET", "POST"])
def assignments():
    assignments = Assignment.query.all()
    return render_template("assignments.html", assignments=assignments)
