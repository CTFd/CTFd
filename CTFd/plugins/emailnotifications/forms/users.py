

from CTFd.forms.users import UserBaseForm, attach_custom_user_fields, attach_user_bracket_field, build_custom_user_fields, build_user_bracket_field
from wtforms import SelectField
from flask_babel import lazy_gettext as _l

def UserEditForm(*args, **kwargs):
    class _UserEditForm(UserBaseForm):
        notifications = SelectField(_l("Email Notifications"),choices=[("true","send"),("false","don't send")])

        @property
        def extra(self):
            return build_custom_user_fields(
                self,
                include_entries=True,
                fields_kwargs=None,
                field_entries_kwargs={"user_id": self.obj.id},
            ) + build_user_bracket_field(self, value=self.obj.bracket_id)

        def __init__(self, *args, **kwargs):
            """
            Custom init to persist the obj parameter to the rest of the form
            """
            super().__init__(*args, **kwargs)
            obj = kwargs.get("obj")
            if obj:
                self.obj = obj

    attach_custom_user_fields(_UserEditForm)
    attach_user_bracket_field(_UserEditForm)

    return _UserEditForm(*args, **kwargs)