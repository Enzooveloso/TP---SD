from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Aluno, Monografia, Professor, Banca
from .forms import AlunoForm, MonografiaForm, ProfessorForm, BancaForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied

def is_admin(user):
    """ Verifica se o usuário é um administrador (staff). """
    return user.is_staff

def is_professor(user):
    """ Verifica se o usuário pertence ao grupo 'Professores'. """
    return user.groups.filter(name='Professores').exists()

def is_aluno(user):
    """ Verifica se o usuário pertence ao grupo 'Alunos'. """
    return user.groups.filter(name='Alunos').exists()

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

class MonografiaCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Monografia
    form_class = MonografiaForm
    template_name = 'monografia_form.html'
    success_url = reverse_lazy('monografia_list')

    def test_func(self):
        return is_professor(self.request.user)

class MonografiaDetailView(DetailView):
    model = Monografia
    template_name = 'core/monografia_detail.html'


class MonografiaUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Monografia
    form_class = MonografiaForm
    template_name = 'monografia_form.html'
    success_url = reverse_lazy('monografia_list')

    def test_func(self):

        monografia = self.get_object()
        user = self.request.user

        if user.is_staff:
            return True
        
        if hasattr(user, 'aluno_profile') and monografia.aluno == user.aluno_profile:
            return True
            
        if hasattr(user, 'professor_profile') and monografia.orientador == user.professor_profile:
            return True

        return False


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

class BancaCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Banca
    form_class = BancaForm
    template_name = 'core/banca_form.html'
    success_url = reverse_lazy('banca_list')

    def test_func(self):
        return is_professor(self.request.user)

class BancaUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Banca
    form_class = BancaForm
    template_name = 'core/banca_form.html'
    success_url = reverse_lazy('banca_list')

    def test_func(self):
        return is_professor(self.request.user)

class BancaDeleteView(DeleteView):
    model = Banca
    template_name = 'core/confirm_delete.html'
    success_url = reverse_lazy('banca_list')

class HomePageView(TemplateView):
    """
    Renderiza a página principal (pública) do sistema.
    """
    template_name = "home.html"


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        user = self.request.user

        if hasattr(user, 'aluno_profile'):
            context['user_type'] = 'Aluno'
            # Usamos um try-except para o caso do aluno ainda não ter uma monografia
            try:
                context['monografia'] = user.aluno_profile.monografia
            except Monografia.DoesNotExist:
                context['monografia'] = None
        
        #  se o usuário TEM um perfil de professor associado
        elif hasattr(user, 'professor_profile'):
            context['user_type'] = 'Professor'
            # BUsca todas as monografias que este professor orienta
            context['monografias_orientadas'] = Monografia.objects.filter(orientador=user.professor_profile)
        
        else:
            context['user_type'] = 'Usuário sem perfil definido'

        return context