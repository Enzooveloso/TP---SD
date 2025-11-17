import logging
from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed,
)
from django.db.models.signals import post_migrate, post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import Monografia, Banca

# Pega (ou cria) um logger chamado 'auditoria' para registrar nossas mensagens.
# Isso é melhor do que usar print(), pois pode ser configurado para salvar em arquivos, etc.
logger = logging.getLogger("auditoria")


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """
    Registra um evento de login bem-sucedido.
    'user' é o objeto do usuário que acabou de fazer login.
    'request' contém informações da requisição, como o IP do usuário.
    """
    ip = request.META.get("REMOTE_ADDR")
    logger.info(
        f"AUDITORIA: Login bem-sucedido para o usuário '{user.username}' do IP [{ip}]"
    )


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    """
    Registra uma tentativa de login mal-sucedida.
    'credentials' é um dicionário contendo os dados usados na tentativa (ex: {'username': 'tentativa'}).
    """
    ip = request.META.get("REMOTE_ADDR")
    username = credentials.get("username")
    logger.warning(
        f"AUDITORIA: Tentativa de login falhou para o usuário '{username}' do IP [{ip}]"
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """
    Registra um evento de logout.
    'user' pode ser None se a sessão simplesmente expirou, então verificamos se ele existe.
    """
    if user:
        ip = request.META.get("REMOTE_ADDR")
        logger.info(f"AUDITORIA: Logout para o usuário '{user.username}' do IP [{ip}]")


@receiver(post_migrate)
def ensure_default_groups(sender, **kwargs):
    """
    Garante que grupos e permissões mínimas existam após migrações.
    """
    if sender.name != "core":
        return

    alunos_group, _ = Group.objects.get_or_create(name="Alunos")
    professores_group, _ = Group.objects.get_or_create(name="Professores")

    content_types = ContentType.objects.get_for_models(Monografia, Banca)

    monografia_perms = Permission.objects.filter(
        content_type=content_types[Monografia],
        codename__in=[
            "add_monografia",
            "change_monografia",
            "view_monografia",
            "can_delete_monografia",
        ],
    )
    banca_perms = Permission.objects.filter(
        content_type=content_types[Banca],
        codename__in=[
            "add_banca",
            "change_banca",
            "delete_banca",
            "view_banca",
        ],
    )

    professores_group.permissions.add(*list(monografia_perms | banca_perms))
    alunos_group.permissions.add(
        *Permission.objects.filter(
            content_type=content_types[Monografia],
            codename__in=["add_monografia", "change_monografia", "view_monografia"],
        )
    )


@receiver(post_save, sender=Monografia)
def audit_monografia(sender, instance, created, **kwargs):
    acao = "CRIOU" if created else "ATUALIZOU"
    autor = getattr(instance.aluno.user, "username", "desconhecido")
    logger.info(
        f"AUDITORIA: {acao} monografia '{instance.titulo}' (aluno: {autor}) "
        f"status: {instance.get_status_display()}"
    )


@receiver(post_delete, sender=Monografia)
def audit_monografia_excluida(sender, instance, **kwargs):
    logger.warning(f"AUDITORIA: EXCLUIU monografia '{instance.titulo}'")


@receiver(post_save, sender=Banca)
def audit_banca(sender, instance, created, **kwargs):
    acao = "AGENDOU" if created else "ATUALIZOU"
    logger.info(
        f"AUDITORIA: {acao} banca para '{instance.monografia.titulo}' em "
        f"{instance.data_defesa} no local '{instance.local_defesa}'"
    )
