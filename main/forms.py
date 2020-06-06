from flask_wtf import Form
from wtforms import TextField, TextAreaField, SubmitField, PasswordField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Length
from wtforms.fields.html5 import DateField, TimeField

class AuthForm(Form):
    #name = TextField('Displayed name', validators = [DataRequired()])
    username = TextField('Username', validators = [DataRequired()])
    password = PasswordField('Password', validators = [DataRequired()])
    submit = SubmitField('Authenticate')

class MeetingForm(Form):
    meetingname = TextField('Meeting name', validators = [DataRequired(), Length(max=100,message="Limit is 100 charecters")])
    info = TextAreaField('Purpose of the meeting and other useful information', validators = [DataRequired(), Length(max=2000,message="Limit is 2000 charecters")])
    duration = TimeField('Duration', format='%H:%M', validators = [DataRequired()])
    available_dates = HiddenField()
    submit = SubmitField('Submit')

class DaysAndHoursForm(Form):
    name = TextField('Displayed name', validators = [DataRequired()])
    selecteddaysandhours = HiddenField()
    submit = SubmitField('Submit')