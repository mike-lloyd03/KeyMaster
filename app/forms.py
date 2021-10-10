"""forms contains all of the forms in the app"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    DateField,
    SelectField,
)
from wtforms.validators import DataRequired, Optional, EqualTo


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


class EditKeyForm(FlaskForm):
    """Form for editing existing keys"""

    description = StringField("Description")
    status = SelectField(
        "Status", choices=["Active", "Inactive"], validate_choice=False
    )
    submit = SubmitField("Save Changes")


class AssignKeyForm(FlaskForm):
    """Form for assigning keys to a user"""

    user = SelectField("User", validators=[DataRequired()])
    key = SelectField("Key", validators=[DataRequired()])
    date_out = DateField("Date Out", validators=[DataRequired()])
    submit = SubmitField("Submit")


class EditAssignmentForm(FlaskForm):
    """Form for editing an existing assignment"""

    user = SelectField("User", validators=[DataRequired()])
    key = SelectField("Key", validators=[DataRequired()])
    date_out = DateField("Date Out", validators=[DataRequired()])
    date_in = DateField("Date In", validators=[Optional()])
    submit = SubmitField("Submit")


class NewUserForm(FlaskForm):
    """Form for creating new users"""

    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")]
    )
    can_login = BooleanField("Can Login?")
    submit = SubmitField("Submit")


class EditUserForm(FlaskForm):
    """Form for editing existing users"""

    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    can_login = BooleanField("Can Login?")
    submit = SubmitField("Submit")
