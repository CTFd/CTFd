from flask_babel import lazy_gettext as _l
from wtforms import SelectField

from CTFd.constants.groups import GroupTypes
from CTFd.forms.fields import SubmitField
from CTFd.forms import BaseForm

class ScoreBoardGroupSelect(BaseForm):
    
    def __init__(self, current="") -> None:
        super().__init__()
        self.current = current

    current = ""

    group_type = SelectField(
        _l("Group Type"),
        choices=[("", "All Groups")] + [
            (i, _l(i)) for i in GroupTypes
        ],
        default = current
    )
    submit = SubmitField("Query")