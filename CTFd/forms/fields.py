from wtforms import SubmitField as _SubmitField


class SubmitField(_SubmitField):
    """
    This custom SubmitField exists because wtforms is dumb.

    See https://github.com/wtforms/wtforms/issues/205, https://github.com/wtforms/wtforms/issues/36
    The .submit() handler in JS will break if the form has an input with the name or id of "submit" so submit fields need to be changed.
    """

    def __init__(self, *args, **kwargs):
        name = kwargs.pop("name", "_submit")
        super().__init__(*args, **kwargs)
        if self.name == "submit" or name:
            self.id = name
            self.name = name
