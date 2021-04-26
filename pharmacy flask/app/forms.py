from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    submit = SubmitField('Find patient')

class AddForm(FlaskForm):
    surname = StringField('surname*', validators=[DataRequired()])
    forename = StringField('forename*', validators=[DataRequired()])
    DOB = StringField('Date of birth*', validators=[DataRequired()])
    Address1 = StringField('Address 1*', validators=[DataRequired()])
    Address2 = StringField('Address 2')
    Town = StringField('Town')
    County = StringField('County')
    Post_code = StringField('Post Code')
    
    submit = SubmitField('Add patient')
    

