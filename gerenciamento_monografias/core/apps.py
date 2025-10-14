from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"


def ready(self):
    """
    Este método é executado pelo Django assim que o app 'core' está pronto.
    É o local recomendado para importar e ativar os sinais.
    """
    import core.signals
