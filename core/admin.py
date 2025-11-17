from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Professor, Aluno, Monografia, Banca


@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ("user", "titulacao", "area_pesquisa")
    search_fields = ("user__username", "user__first_name", "user__last_name", "area_pesquisa")


@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ("user", "matricula")
    search_fields = ("user__username", "user__first_name", "user__last_name", "matricula")


@admin.register(Monografia)
class MonografiaAdmin(SimpleHistoryAdmin):
    list_display = ("titulo", "aluno", "orientador", "status", "data_publicacao")
    list_filter = ("status", "data_publicacao")
    search_fields = ("titulo", "aluno__user__username", "orientador__user__username")
    history_list_display = ["status"]


@admin.register(Banca)
class BancaAdmin(admin.ModelAdmin):
    list_display = ("monografia", "data_defesa", "local_defesa")
    list_filter = ("data_defesa",)
    search_fields = ("monografia__titulo", "local_defesa")
