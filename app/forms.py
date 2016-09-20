from flask_wtf import Form
from wtforms.fields import HiddenField, StringField

class ResponseForm(Form):
    discard_selection = HiddenField('discard_selection')
    # current_status = HiddenField('current_status')
