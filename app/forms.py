"""forms contains all of the forms in the app"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    DateField,
    SelectField,
    SelectMultipleField,
    ValidationError,
)
from wtforms.validators import DataRequired, Optional, EqualTo

from app.models import User


class LoginForm(FlaskForm):
    """Form for logging users into the app"""

    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    # remember_me = BooleanField("Remember me")
    submit = SubmitField("Sign In")


class NewKeyForm(FlaskForm):
    """Form for creating new keys"""

    name = StringField("Key Name", validators=[DataRequired()])
    description = StringField("Description")
    submit = SubmitField("Add Key")
    cancel = SubmitField("Cancel", render_kw={"formnovalidate": True})


class EditKeyForm(FlaskForm):
    """Form for editing existing keys"""

    description = StringField("Description")
    status = SelectField(
        "Status", choices=["Active", "Inactive"], validate_choice=False
    )
    submit = SubmitField("Save Changes")
    delete = SubmitField("Delete Key")
    cancel = SubmitField("Cancel", render_kw={"formnovalidate": True})


class AssignKeyForm(FlaskForm):
    """Form for assigning keys to a user"""

    # user = SelectField("User", validators=[DataRequired()])
    user = SelectMultipleField("User", validators=[DataRequired()])
    key = SelectMultipleField("Key", validators=[DataRequired()])
    date_out = DateField("Date Out", validators=[DataRequired()])
    submit = SubmitField("Assign Key")
    cancel = SubmitField("Cancel", render_kw={"formnovalidate": True})


class EditAssignmentForm(FlaskForm):
    """Form for editing an existing assignment"""

    user = SelectField("User", validators=[DataRequired()])
    key = SelectField("Key", validators=[DataRequired()])
    date_out = DateField("Date Out", validators=[DataRequired()])
    date_in = DateField("Date In", validators=[Optional()])
    submit = SubmitField("Save Changes")
    delete = SubmitField("Delete Assignment")
    cancel = SubmitField("Cancel", render_kw={"formnovalidate": True})


class NewUserForm(FlaskForm):
    """Form for creating new users"""

    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    display_name = StringField("Display Name")
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")]
    )
    can_login = BooleanField("Can Login?")
    submit = SubmitField("Create User")
    cancel = SubmitField("Cancel", render_kw={"formnovalidate": True})

    def __init__(self):
        super(NewUserForm, self).__init__()

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError(f"Username is already in use.")

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError(f"Email address is already in use.")


class EditUserForm(FlaskForm):
    """Form for editing existing users"""

    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    display_name = StringField("Display Name")
    can_login = BooleanField("Can Login?")
    submit = SubmitField("Save Changes")
    delete = SubmitField("Delete User")
    cancel = SubmitField("Cancel", render_kw={"formnovalidate": True})


class ConfirmForm(FlaskForm):
    """Form for confirming changes"""

    yes = SubmitField("Yes")
    no = SubmitField("No")
