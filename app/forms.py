from flask_wtf import Form
from wtforms.fields import HiddenField

class ResponseForm(Form):
    """
    Create form object with single object for discards, submitted when user
    makes a move
    """
    discard_selection = HiddenField('discard_selection')
