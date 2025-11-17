from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        """
        Importa os sinais assim que o app é carregado para garantir
        auditoria e configuração de permissões/grupos.
        """
        from . import signals  # noqa: F401
