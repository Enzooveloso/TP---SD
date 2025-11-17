import re
from datetime import date
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class PasswordComplexityValidator:
    """
    Exige senha com comprimento mínimo, letra maiúscula, minúscula, número e caractere especial.
    """

    def validate(self, password, user=None):
        errors = []
        if len(password) < 10:
            errors.append("ter pelo menos 10 caracteres")
        if not re.search(r"[A-Z]", password):
            errors.append("incluir letra maiúscula")
        if not re.search(r"[a-z]", password):
            errors.append("incluir letra minúscula")
        if not re.search(r"\d", password):
            errors.append("incluir número")
        if not re.search(r"[^\w\s]", password):
            errors.append("incluir caractere especial")

        if errors:
            raise ValidationError(
                _("A senha deve %(requisitos)s."),
                code="password_too_weak",
                params={"requisitos": ", ".join(errors)},
            )

    def get_help_text(self):
        return _(
            "A senha deve ter pelo menos 10 caracteres e conter letra maiúscula, "
            "letra minúscula, número e caractere especial."
        )


def validate_future_date(value):
    if not value:
        return
    current = date.today()
    candidate = value.date() if hasattr(value, "date") else value
    if candidate < current:
        raise ValidationError(_("A data não pode estar no passado."))


def validate_pdf_extension(uploaded_file):
    if not uploaded_file:
        return
    filename = getattr(uploaded_file, "name", "") or ""
    if not filename.lower().endswith(".pdf"):
        raise ValidationError(_("Envie apenas arquivos PDF."))
