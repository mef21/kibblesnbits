from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug.utils import secure_filename
from wtforms import StringField, IntegerField, SubmitField, TextAreaField, PasswordField, SelectField, RadioField
from wtforms.validators import (
    InputRequired,
    DataRequired,
    NumberRange,
    Length,
    Email,
    EqualTo,
    ValidationError,
)
import pyotp

from .models import User


class SearchForm(FlaskForm):
    search_query = StringField(
        "Query", validators=[InputRequired(),Length(min=1, max=100)]
    )
    submit = SubmitField("Search")


class MovieReviewForm(FlaskForm):
    text = TextAreaField(
        "Comment", validators=[InputRequired(), Length(min=5, max=500)]
    )
    submit = SubmitField("Enter Comment")


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username", validators=[InputRequired(), Length(min=1, max=40)]
    )
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[InputRequired(), EqualTo("password")]
    )
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        user = User.objects(username=username.data).first()
        if user is not None:
            raise ValidationError("Username is taken")

    def validate_email(self, email):
        user = User.objects(email=email.data).first()
        if user is not None:
            raise ValidationError("Email is taken")
    def validate_password(self, password):
        boo1 = (len(password.data) >= 8)
        hasnum = False
        hassym = False
        hasupp = False
        haslower = False
        spchar = "!@#$%^&*()-+?_=<>"
        for c in password.data:
            if c.isdigit():
                hasnum = True
            elif c in spchar:
                hassym = True
            elif c.islower():
                haslower = True
            elif c.isupper():
                hasupp = True
        if(boo1 and hasnum and hassym and hasupp and haslower):
            "cool"
        else:
            raise ValidationError("Password does not fit requirements!")

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")
    token = StringField('Token', validators=[InputRequired(), Length(min=6, max=6)])
    def validate_token(self, token):
        user = User.objects(username=self.username.data).first()
        if user is not None:
            tok_verified = pyotp.TOTP(user.otp_secret).verify(token.data)
            if not tok_verified:
                raise ValidationError("Invalid Token")


class UpdateUsernameForm(FlaskForm):
    username = StringField(
        "Username", validators=[InputRequired(), Length(min=1, max=40)]
    )
    submit = SubmitField("Update Username")

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.objects(username=username.data).first()
            if user is not None:
                raise ValidationError("That username is already taken")

class UpdateProfilePicForm(FlaskForm):
    propic = FileField('Profile Picture', validators=[
        FileRequired(), 
        FileAllowed(['jpg', 'png'], 'Images Only!')
    ])
    submit = SubmitField('Update')

    
class MainPageForm(FlaskForm):
    text = TextAreaField(
        "Text", validators=[InputRequired(), Length(min=1, max=140)]
    )
    propic = FileField('Attach a photo / image here', validators=[ 
        FileAllowed(['jpg', 'png'], 'Images Only!')
    ])
    submit = SubmitField("Post to the Main Page")

class DailyDogPoll(FlaskForm):
    dog_choice = RadioField("Image Selection",choices=["1","2"])
    submit = SubmitField("Submit today's choice")
