from django import template
from django.contrib.auth.models import Group

register = template.Library()


@register.filter(name="is_professor")
def is_professor(user):
    """
    Verifica no template se um usuário pertence ao grupo 'Professores'.
    Uso: {{ user|is_professor }}
    """
    return user.groups.filter(name="Professores").exists()


@register.filter(name="is_aluno")
def is_aluno(user):
    """
    Verifica no template se um usuário pertence ao grupo 'Alunos'.
    Uso: {{ user|is_aluno }}
    """
    return user.groups.filter(name="Alunos").exists()
