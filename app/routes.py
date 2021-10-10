from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, login_required, logout_user

from app import app, db
from app.forms import (
    LoginForm,
    NewKeyForm,
    EditKeyForm,
    AssignKeyForm,
    EditAssignmentForm,
    LoginForm,
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


def get_headings_rows(obj_list, heading_map={}):
    """
    Generates a list of headings and a list of rows from a list of
    SQLAlchemy objects

    heading_map can be used to select which object attributes should be
    added to the rows and optionally how the row heading for that
    attribute should be renamed. If it is a dict, it will be used for
    remaping column names. If it is a tuple or list, it will be used for
    filtering object attributes.

    Example:
    `heading_map = {"obj_attribute1": "Heading Name1",
                    "obj_attribute2": "Heading Name2"}`

    To specify attributes without renaming them, the value can be None:
    `heading_map = {"obj_attribute1": "Heading Name1",
                    "obj_attribute2": None}`
    """
    if isinstance(heading_map, (list, tuple)):
        is_dict = False
        headings = list(heading_map)
    else:
        is_dict = True
        if heading_map:
            headings = [v if v else k for k, v in heading_map.items()]
        else:
            headings = [
                h for h in vars(obj_list[0]).keys() if not str(h).startswith("_")
            ]

    if is_dict and heading_map:
        eval_headings = list(heading_map.keys())
    elif is_dict and not heading_map:
        eval_headings = headings
    elif not is_dict:
        eval_headings = headings

    rows = []
    for obj in obj_list:
        row = []
        for heading in eval_headings:
            row.append(getattr(obj, heading))
        rows.append(row)
    return (headings, rows)


@app.route("/")
@app.route("/index")
@login_required
def index():
    query_results = (
        Assignment.query.filter_by(date_in=None).order_by(Assignment.user).all()
    )

    heading_map = {"user": "User", "key": "Key Assigned"}
    headings, rows = get_headings_rows(query_results, heading_map)
    print(headings, rows)
    return render_template("index.html", headings=headings, rows=rows)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if (
            user is None
            or not user.can_login
            or not user.check_password(form.password.data)
        ):
            flash("Invalid login credentials")
            return redirect(url_for("login"))
        login_user(user)
        return redirect(url_for("index"))
    return render_template("quick_form.html", form=LoginForm(), title="Login")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/keys")
@login_required
def keys():
    keys = Key.query.all()
    return render_template("keys.html", keys=keys)


@app.route("/add_key", methods=["GET", "POST"])
@login_required
def add_key():
    form = NewKeyForm()
    if form.validate_on_submit():
        key = Key(name=form.name.data, description=form.description.data)
        db.session.add(key)
        db.session.commit()
        flash(f'Key "{key.name}" added')
        return redirect(url_for("keys"))
    return render_template("quick_form.html", form=form, title="New Key")


@app.route("/edit_key", methods=["GET", "POST"])
@login_required
def edit_key():
    key_name = request.args.get("name")
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
@login_required
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
@login_required
def assignments():
    assignments = Assignment.query.all()
    return render_template("assignments.html", assignments=assignments)


@app.route("/edit_assignment", methods=["GET", "POST"])
@login_required
def edit_assignment():
    assignment_id = request.args.get("id")
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
