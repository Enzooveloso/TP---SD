from django.contrib import admin
from .models import Professor, Aluno, Monografia, Banca

admin.site.register(Professor)
admin.site.register(Aluno)
admin.site.register(Monografia)
admin.site.register(Banca)
