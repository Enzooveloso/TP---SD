from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Aluno, Monografia, Professor, Banca
from .forms import AlunoForm, MonografiaForm, ProfessorForm, BancaForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

# CRUD Monografia
class MonografiaListView(ListView):
    model = Monografia
    template_name = 'monografia_list.html'
    context_object_name = 'monografias'
    paginate_by = 10  # Paginação

    # função de busca para diferentes critérios
    def get_queryset(self):
        queryset = super().get_queryset() # pega todos os objetos
        query = self.request.GET.get('q') # parâmetro de busca da URL
        if query:
             queryset = queryset.filter(
                Q(titulo__icontains=query) |
                Q(resumo__icontains=query) |
                Q(abstract__icontains=query) |
                Q(palavras_chave__icontains=query) |
                Q(orientador__user__first_name__icontains=query) |
                Q(orientador__user__last_name__icontains=query) |
                Q(aluno__user__first_name__icontains=query) |
                Q(aluno__user__last_name__icontains=query)
            )
        return queryset.order_by('-data_publicacao') # ordenacao por mais recente

class MonografiaCreateView(CreateView):
    model = Monografia
    template_name = 'monografia_form.html'
    form_class = MonografiaForm
    success_url = reverse_lazy('monografia_list')

class MonografiaDetailView(DetailView):
    model = Monografia
    template_name = 'core/monografia_detail.html'


class MonografiaUpdateView(UpdateView):
    model = Monografia
    template_name = 'monografia_form.html'
    form_class = MonografiaForm
    success_url = reverse_lazy('monografia_list')


class MonografiaDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Monografia
    template_name = 'monografia_confirm_delete.html'
    success_url = reverse_lazy('monografia_list')

    permission_required = 'core.can_delete_monografia'

    raise_exception = True 

#CRUD Aluno
class AlunoListView(ListView):
    model = Aluno
    template_name = 'aluno_list.html'
    context_object_name = 'alunos'

class AlunoCreateView(CreateView):
    model = Aluno
    template_name = 'aluno_form.html'
    form_class = AlunoForm
    success_url = reverse_lazy('aluno_list')

class AlunoUpdateView(UpdateView):
    model = Aluno
    template_name = 'aluno_form.html'
    form_class = AlunoForm
    success_url = reverse_lazy('aluno_list')

class AlunoDeleteView(DeleteView):
    model = Aluno
    template_name = 'aluno_confirm_delete.html'
    success_url = reverse_lazy('aluno_list')

#CRUD Professor
class ProfessorListView(ListView):
    model = Professor
    template_name = 'professor_list.html'
    context_object_name = 'professores'

class ProfessorCreateView(CreateView):
    model = Professor
    template_name = 'professor_form.html'
    form_class = ProfessorForm
    success_url = reverse_lazy('professor_list')

class ProfessorUpdateView(UpdateView):
    model = Professor
    template_name = 'professor_form.html'
    form_class = ProfessorForm
    success_url = reverse_lazy('professor_list')

class ProfessorDeleteView(DeleteView):
    model = Professor
    template_name = 'professor_confirm_delete.html'
    success_url = reverse_lazy('professor_list')

#CRUD Banca
class BancaListView(ListView):
    model = Banca
    template_name = 'core/banca_list.html'
    context_object_name = 'bancas'

class BancaDetailView(DetailView):
    model = Banca
    template_name = 'core/banca_detail.html'

class BancaCreateView(CreateView):
    model = Banca
    form_class = BancaForm
    template_name = 'core/banca_form.html'
    success_url = reverse_lazy('banca_list')

class BancaUpdateView(UpdateView):
    model = Banca
    form_class = BancaForm
    template_name = 'core/banca_form.html'
    success_url = reverse_lazy('banca_list')

class BancaDeleteView(DeleteView):
    model = Banca
    template_name = 'core/confirm_delete.html'
    success_url = reverse_lazy('banca_list')
