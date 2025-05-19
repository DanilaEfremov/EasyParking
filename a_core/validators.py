import re  # noqa: D100, EXE002

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from accounts.models import CustomUser


class UppercasePasswordValidator:
    """Валидатор пароля."""

    def validate(self, password: str, user: CustomUser=None) -> None:  # noqa: ARG002
        """Валидатор пароля."""
        if not re.search(r"[A-Z]", password):
            raise ValidationError(
                _("Пароль должен содержать хотя бы одну заглавную букву."),
                code="password_no_upper",
            )

    def get_help_text(self) -> str:  # noqa: D102
        return _("Ваш пароль должен содержать хотя бы одну заглавную букву.")
