from flask_wtf import FlaskForm
from wtforms import StringField
from wtform.validators import DataRequired, Length

class RegestrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=5, max=20)])
    password = StringField('Password', validators=[DataRequired(), Length(min=8, max=128)])
    submit = SubmitField('Register!')
