from wtforms import (
    BooleanField,
    HiddenField,
    MultipleFileField,
    SelectField,
    StringField,
    TextAreaField,
)
from wtforms.validators import InputRequired

from CTFd.forms import BaseForm


class PageEditForm(BaseForm):
    title = StringField(
        "Title", description="This is the title shown on the navigation bar"
    )
    route = StringField(
        "Route",
        description="This is the URL route that your page will be at (e.g. /page). You can also enter links to link to that page.",
    )
    draft = BooleanField("Draft")
    hidden = BooleanField("Hidden")
    auth_required = BooleanField("Authentication Required")
    content = TextAreaField("Content")
    format = SelectField(
        "Format",
        choices=[("markdown", "Markdown"), ("html", "HTML")],
        default="markdown",
        validators=[InputRequired()],
        description="The markup format used to render the page",
    )
    link_target = SelectField(
        "Target",
        choices=[("", "Current Page"), ("_blank", "New Tab")],
        default="",
        validators=[],
        description="Context to open page in",
    )


class PageFilesUploadForm(BaseForm):
    file = MultipleFileField(
        "Upload Files",
        description="Attach multiple files using Control+Click or Cmd+Click.",
        validators=[InputRequired()],
    )
    type = HiddenField("Page Type", default="page", validators=[InputRequired()])
