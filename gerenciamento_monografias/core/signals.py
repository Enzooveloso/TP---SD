from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
import logging

# Pega (ou cria) um logger chamado 'auditoria' para registrar nossas mensagens.
# Isso é melhor do que usar print(), pois pode ser configurado para salvar em arquivos, etc.
logger = logging.getLogger('auditoria')

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """
    Registra um evento de login bem-sucedido.
    'user' é o objeto do usuário que acabou de fazer login.
    'request' contém informações da requisição, como o IP do usuário.
    """
    ip = request.META.get('REMOTE_ADDR')
    logger.info(f"AUDITORIA: Login bem-sucedido para o usuário '{user.username}' do IP [{ip}]")

@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    """
    Registra uma tentativa de login mal-sucedida.
    'credentials' é um dicionário contendo os dados usados na tentativa (ex: {'username': 'tentativa'}).
    """
    ip = request.META.get('REMOTE_ADDR')
    username = credentials.get('username')
    logger.warning(f"AUDITORIA: Tentativa de login falhou para o usuário '{username}' do IP [{ip}]")

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """
    Registra um evento de logout.
    'user' pode ser None se a sessão simplesmente expirou, então verificamos se ele existe.
    """
    if user:
        ip = request.META.get('REMOTE_ADDR')
        logger.info(f"AUDITORIA: Logout para o usuário '{user.username}' do IP [{ip}]")