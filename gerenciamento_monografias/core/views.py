from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Aluno, Monografia, Professor, Banca
from .forms import AlunoForm, MonografiaForm, ProfessorForm, BancaForm

# CRUD Monografia
class MonografiaListView(ListView):
    model = Monografia
    template_name = 'monografia_list.html'
    context_object_name = 'monografias'


class MonografiaCreateView(CreateView):
    model = Monografia
    template_name = 'monografia_form.html'
    form_class = MonografiaForm
    success_url = reverse_lazy('monografia_list')


class MonografiaUpdateView(UpdateView):
    model = Monografia
    template_name = 'monografia_form.html'
    form_class = MonografiaForm
    success_url = reverse_lazy('monografia_list')


class MonografiaDeleteView(DeleteView):
    model = Monografia
    template_name = 'monografia_confirm_delete.html'
    success_url = reverse_lazy('monografia_list')

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
