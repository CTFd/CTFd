from wtforms import HiddenField, MultipleFileField
from wtforms.validators import InputRequired

from CTFd.forms import BaseForm


class PageFilesUploadForm(BaseForm):
    file = MultipleFileField(
        "Upload Files",
        description="Attach multiple files using Control+Click or Cmd+Click.",
        validators=[InputRequired()],
    )
    type = HiddenField("Page Type", default="page", validators=[InputRequired()])
