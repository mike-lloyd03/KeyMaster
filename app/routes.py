from flask import render_template, flash, redirect, url_for, request
from app import app, db

from app.forms import (
    LoginForm,
    NewKeyForm,
    EditKeyForm,
    AssignKeyForm,
    EditAssignmentForm,
)
from app.models import Key, User, Assignment

from datetime import datetime


def add_form_choices(form):
    """Creates form selection choices from the Users table and the Keys table"""
    form.user.choices = [u.username for u in User.query.order_by(User.username).all()]
    form.key.choices = [
        k.name for k in Key.query.order_by(Key.name).filter_by(status="Active").all()
    ]
    return form


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
        db.session.add(key)
        db.session.commit()
        flash(f'Key "{key.name}" added')
        return redirect(url_for("keys"))
    return render_template("quick_form.html", form=form, title="New Key")


@app.route("/edit_key/<key_name>", methods=["GET", "POST"])
def edit_key(key_name):
    key = Key.query.filter_by(name=key_name).first_or_404()
    form = EditKeyForm()
    form.description.data = key.description
    form.status.data = key.status
    if form.validate_on_submit():
        key.description = request.form["description"]
        key.status = request.form["status"]
        db.session.commit()
        flash(f'Key "{key.name}" updated')
        return redirect(url_for("keys"))
    return render_template(
        "quick_form.html", form=form, title="Edit Key", subtitle=key.name
    )


@app.route("/assign_key", methods=["GET", "POST"])
def assign_key():
    form = add_form_choices(AssignKeyForm())
    form.user.choices = [u.username for u in User.query.all()]
    form.key.choices = [k.name for k in Key.query.all()]
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


@app.route("/edit_assignment/<assignment_id>", methods=["GET", "POST"])
def edit_assignment(assignment_id):
    assignment = Assignment.query.filter_by(id=assignment_id).first_or_404()

    form = add_form_choices(EditAssignmentForm())
    form.user.data = assignment.user
    form.key.data = assignment.key
    form.date_out.data = assignment.date_out
    form.date_in.data = assignment.date_in

    if form.validate_on_submit():
        assignment.user = request.form["user"]
        assignment.key = request.form["key"]
        assignment.date_out = datetime.strptime(request.form["date_out"], "%Y-%m-%d")
        assignment.date_in = (
            datetime.strptime(request.form["date_in"], "%Y-%m-%d") or None
        )
        db.session.commit()
        flash("Assignment updated")
        return redirect(url_for("assignments"))

    return render_template("quick_form.html", form=form, title="Edit Assignment")
