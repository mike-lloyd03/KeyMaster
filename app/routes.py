from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, login_required, logout_user

from app import app, db
from app.forms import (
    LoginForm,
    NewKeyForm,
    EditKeyForm,
    AssignKeyForm,
    EditAssignmentForm,
    NewUserForm,
    EditUserForm,
    ConfirmForm,
)
from app.models import Key, User, Assignment

############################
# Functions
############################

types = {"key": Key, "user": User, "assignment": Assignment}


def add_form_choices(form):
    """Creates form selection choices from the Users table and the Keys table"""
    form.user.choices = [
        (u.username, u.display_name or u.username)
        for u in User.query.order_by(User.username).all()
    ]
    form.key.choices = [
        (k.name, k.name)
        for k in Key.query.order_by(Key.name).filter_by(status="Active").all()
    ]
    return form


def get_headings_rows(obj_list, heading_map=None):
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


def get_user_dict():
    """
    Returns dictionary of {username: display_name} for all users in
    the Users tables.
    """
    user_list = User.query.all()
    return {user.username: user.display_name for user in user_list if user.display_name}


############################
# Routes
############################


@app.route("/")
@app.route("/index")
@login_required
def index():
    query_results = (
        Assignment.query.filter_by(date_in=None)
        .order_by(Assignment.user, Assignment.key)
        .all()
    )
    user_dict = get_user_dict()

    data = {}
    for r in query_results:
        username = user_dict.get(r.user, r.user)
        if data.get(username):
            data[username] += f", {r.key}"
        else:
            data[username] = str(r.key)

    headings = ["User", "Assigned Keys"]

    # heading_map = {"display_name": "User", "key": "Key Assigned"}
    # headings, rows = get_headings_rows(query_results, heading_map)
    # return render_template("index.html", headings=headings, rows=rows)
    return render_template(
        "index.html",
        headings=headings,
        rows=[[k, v] for k, v in data.items()],
    )


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
    key_list = Key.query.all()
    return render_template("keys.html", keys=key_list)


@app.route("/add_key", methods=["GET", "POST"])
@login_required
def add_key():
    form = NewKeyForm()

    if request.method == "POST":
        if form.cancel.data:
            return redirect(url_for("keys"))

    if form.validate_on_submit():

        if form.submit.data:
            if Key.query.get(form.name.data):
                flash(f'Key "{form.name.data}" already exists.', "danger")
            else:
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
    key = Key.query.filter_by(name=key_name).first()
    if not key:
        return render_template("404.html"), 404
    form = EditKeyForm(description=key.description, status=key.status)

    if request.method == "POST":
        if form.cancel.data:
            return redirect(url_for("keys"))

    if form.validate_on_submit():
        if form.delete.data:
            return redirect(url_for("confirm_delete", item=key_name, model="key"))

        key.description = form.description.data
        key.status = form.status.data
        db.session.commit()
        flash(f'Key "{key.name}" updated')
        return redirect(url_for("keys"))

    return render_template(
        "quick_form.html", form=form, title="Edit Key", subtitle=key.name
    )


@app.route("/assignments", methods=["GET", "POST"])
@login_required
def assignments():
    assignment_list = Assignment.query.all()
    user_dict = get_user_dict()
    return render_template(
        "assignments.html", assignments=assignment_list, users=user_dict
    )


@app.route("/assign_key", methods=["GET", "POST"])
@login_required
def assign_key():
    form = add_form_choices(AssignKeyForm())

    if request.method == "POST":
        if form.cancel.data:
            return redirect(url_for("assignments"))

    if form.validate_on_submit():
        for key in form.key.data:
            assignment = Assignment(
                user=form.user.data, key=key, date_out=form.date_out.data
            )
            db.session.add(assignment)
        db.session.commit()
        flash("Key assigned")
        return redirect(url_for("assignments"))

    return render_template("quick_form.html", form=form, title="Assign Key")


@app.route("/edit_assignment", methods=["GET", "POST"])
@login_required
def edit_assignment():
    assignment_id = request.args.get("id")
    assignment = Assignment.query.filter_by(id=assignment_id).first()
    if not assignment:
        return render_template("404.html"), 404

    form = add_form_choices(
        EditAssignmentForm(
            user=assignment.user,
            key=assignment.key,
            date_out=assignment.date_out,
            date_in=assignment.date_in,
        )
    )

    if request.method == "POST":
        if form.cancel.data:
            return redirect(url_for("assignments"))

    if form.validate_on_submit():
        if form.delete.data:
            return redirect(
                url_for("confirm_delete", item=assignment_id, model="assignment")
            )

        assignment.user = form.user.data
        assignment.key = form.key.data
        assignment.date_out = form.date_out.data
        assignment.date_in = form.date_in.data
        db.session.commit()
        flash("Assignment updated")
        return redirect(url_for("assignments"))

    return render_template("quick_form.html", form=form, title="Edit Assignment")


@app.route("/users")
@login_required
def users():
    user_list = User.query.order_by(User.username).all()
    return render_template("users.html", users=user_list)


@app.route("/add_user", methods=["GET", "POST"])
@login_required
def add_user():
    form = NewUserForm()

    if request.method == "POST":
        if form.cancel.data:
            return redirect(url_for("users"))

    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            print("Existing user:", User.query.get(form.username.data))
            flash(f'User "{form.username.data}" already exists', "danger")
        else:
            user = User(
                username=form.username.data,
                email=form.email.data,
                display_name=form.display_name.data,
                can_login=form.can_login.data,
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash(f'User "{user.username}" created')
        return redirect(url_for("users"))

    return render_template("quick_form.html", form=form, title="Add User")


@app.route("/edit_user", methods=["GET", "POST"])
@login_required
def edit_user():
    user_id = request.args.get("id")
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return render_template("404.html"), 404
    form = EditUserForm(
        username=user.username,
        email=user.email,
        display_name=user.display_name,
        can_login=user.can_login,
    )

    if request.method == "POST":
        if form.cancel.data:
            return redirect(url_for("users"))

    if form.validate_on_submit():
        if form.delete.data:
            return redirect(url_for("confirm_delete", item=user_id, model="user"))

        user.username = form.username.data
        user.email = form.email.data
        user.display_name = form.display_name.data
        user.can_login = form.can_login.data
        db.session.commit()
        flash(f'User "{user.username}" updated.')
        return redirect(url_for("users"))

    return render_template("quick_form.html", form=form, title="Edit User")


@app.route("/confirm_delete", methods=["GET", "POST"])
@login_required
def confirm_delete():
    form = ConfirmForm()

    model_name = request.args.get("model")
    item_name = request.args.get("item")
    model = types.get(model_name)
    item = model.query.get(item_name)
    if model_name == "user":
        item_name = item.display_name if item.display_name else item.username

    if not model or not item:
        return render_template("404.html"), 404

    if form.validate_on_submit():
        if form.yes.data:
            if model_name == "key":
                # Check if key is currently assigned to users
                if Assignment.query.filter_by(date_in=None, key=item_name).all():
                    flash(
                        f'Key "{item_name}" is still checked out to users and cannot be deleted.',
                        "danger",
                    )
                else:
                    flash(f'Key {item_name}" deleted.')
                    db.session.delete(item)
                    db.session.commit()

            elif model_name == "user":
                # Check if user has any keys checked out
                if Assignment.query.filter_by(date_in=None, user=item_name).all():
                    flash(
                        f'User "{item_name}" still has keys checked out and cannot be deleted.',
                        "danger",
                    )
                else:
                    flash(f'User "{item_name}" deleted.')
                    db.session.delete(item)
                    db.session.commit()
            elif model_name == "assignment":
                flash("Assignment deleted.")
                db.session.delete(item)
                db.session.commit()

            else:
                flash(f'The item "{model_name}" is not recognized.', "danger")

        return redirect(url_for(f"{model_name}s"))

    return render_template(
        "quick_form.html",
        form=form,
        title=f"Delete {model_name.capitalize()}",
        subtitle=f'Are you sure you want to delete {model_name} "{item_name}"?',
    )
