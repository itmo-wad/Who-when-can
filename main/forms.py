from flask_wtf import Form
from wtforms import TextField, TextAreaField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired

class SignUpForm(Form):
    username = TextField('User Name', validators= [ DataRequired()])
    password = PasswordField('Password',validators=[ DataRequired()])
    submit = SubmitField('Sign Up')


class SignInForm(Form):
    username = TextField('Username', validators = [DataRequired()])
    password = PasswordField('Password', validators = [DataRequired()])
    submit = SubmitField('Sign In')

class ChangeForm(Form):
    password = TextField('Password', validators = [DataRequired()])
    submit = SubmitField('Change Pass')