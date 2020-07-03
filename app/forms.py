from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired


class CalculateForm(FlaskForm):
    option = SelectField(u'Input Data for Scenario One', choices=[])
    option2 = SelectField(u'Input Data for Scenario Two', choices=[])
    calculate = SubmitField('Calculate')
    show = SubmitField('Show Data')

class CreateForm(FlaskForm):
    option = SelectField(u'Base Data for the new Scenario', choices=[])
    create = SubmitField('Create New Scenario with base data')
    createNew = SubmitField('Create New Scenario with own data')

class CreateNewForm(FlaskForm):
    createNew = SubmitField('Use these parameters')

class EditForm(FlaskForm):
    emissiongoal = StringField('Emission Goal')
    eb = StringField('Ergebnisbeitrag')
    #eb = [[StringField('Ergebnisbeitrag') for x in range(4)] for y in range(8)]


