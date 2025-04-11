import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class UppercasePasswordValidator:
    def validate(self, password, user=None):
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _("Пароль должен содержать хотя бы одну заглавную букву."),
                code='password_no_upper',
            )

    def get_help_text(self):
        return _("Ваш пароль должен содержать хотя бы одну заглавную букву.")
