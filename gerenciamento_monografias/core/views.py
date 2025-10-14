from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
    TemplateView,
)
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Aluno, Monografia, Professor, Banca
from .forms import AlunoForm, MonografiaForm, ProfessorForm, BancaForm
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UserPassesTestMixin,
)
from django.core.exceptions import PermissionDenied


def is_admin(user):
    return user.is_staff


def is_professor(user):
    return user.groups.filter(name="Professores").exists()


def is_aluno(user):
    return user.groups.filter(name="Alunos").exists()


# --- CRUD Monografia ---
class MonografiaListView(LoginRequiredMixin, ListView):
    model = Monografia
    template_name = "core/monografia_list.html"
    context_object_name = "monografias"
    paginate_by = 10

    def get_queryset(self):

        queryset = super().get_queryset()
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(
                Q(titulo__icontains=query)
                | Q(resumo__icontains=query)
                | Q(abstract__icontains=query)
                | Q(palavras_chave__icontains=query)
                | Q(orientador__user__first_name__icontains=query)
                | Q(orientador__user__last_name__icontains=query)
                | Q(aluno__user__first_name__icontains=query)
                | Q(aluno__user__last_name__icontains=query)
            )
        return queryset.order_by("-data_publicacao")


class MonografiaCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Monografia
    form_class = MonografiaForm
    template_name = "core/monografia_form.html"
    success_url = reverse_lazy("monografia_list")

    def test_func(self):
        """
        Verifica duas condições:
        1. O usuário está no grupo 'Alunos'?
        2. O perfil de Aluno (com matrícula) já foi criado para este usuário?
        """
        user = self.request.user
        return user.groups.filter(name="Alunos").exists() and hasattr(
            user, "aluno_profile"
        )

    def form_valid(self, form):
        if (
            hasattr(self.request.user, "aluno_profile")
            and Monografia.objects.filter(
                aluno=self.request.user.aluno_profile
            ).exists()
        ):
            form.add_error(None, "Você já possui uma monografia cadastrada.")
            return self.form_invalid(form)

        form.instance.aluno = self.request.user.aluno_profile
        return super().form_valid(form)


class MonografiaDetailView(LoginRequiredMixin, DetailView):
    model = Monografia
    template_name = "core/monografia_detail.html"

    def get_context_data(self, **kwargs):
        """
        Adiciona variáveis de permissão ao contexto para simplificar o template.
        """
        context = super().get_context_data(**kwargs)
        monografia = self.get_object()
        user = self.request.user

        can_manage_monografia = False
        can_manage_banca = False

        if user.is_staff:
            can_manage_monografia = True
        elif hasattr(user, "aluno_profile") and monografia.aluno == user.aluno_profile:
            can_manage_monografia = True
        elif hasattr(user, "professor_profile"):
            professor_profile = user.professor_profile
            if monografia.orientador == professor_profile or (
                monografia.coorientador and monografia.coorientador == professor_profile
            ):
                can_manage_monografia = True

        # Lógica de permissão para gerenciar a BANCA (agendar, editar)
        if user.is_staff:
            can_manage_banca = True
        elif hasattr(user, "professor_profile"):
            professor_profile = user.professor_profile
            if monografia.orientador == professor_profile or (
                monografia.coorientador and monografia.coorientador == professor_profile
            ):
                can_manage_banca = True

        context["can_manage_monografia"] = can_manage_monografia
        context["can_manage_banca"] = can_manage_banca
        return context


class MonografiaUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Monografia
    form_class = MonografiaForm
    template_name = "core/monografia_form.html"
    success_url = reverse_lazy("monografia_list")

    def test_func(self):
        monografia = self.get_object()
        user = self.request.user

        # 1. Admin pode tudo.
        if user.is_staff:
            return True

        # 2. O aluno dono do trabalho pode editar.
        if hasattr(user, "aluno_profile") and monografia.aluno == user.aluno_profile:
            return True

        # 3. O orientador OU o coorientador podem editar.
        if hasattr(user, "professor_profile"):
            professor_profile = user.professor_profile
            if monografia.orientador == professor_profile:
                return True
            # Adicionamos a verificação para o coorientador (que pode ser nulo)
            if monografia.coorientador and monografia.coorientador == professor_profile:
                return True

        # Se nenhuma das condições for atendida, nega o acesso.
        return False


class MonografiaDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Monografia
    template_name = "core/monografia_confirm_delete.html"
    success_url = reverse_lazy("monografia_list")
    permission_required = "core.can_delete_monografia"
    raise_exception = True


# --- CRUD Aluno ---
class AlunoListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Aluno
    template_name = "core/aluno_list.html"
    context_object_name = "alunos"

    def test_func(self):
        return self.request.user.is_staff


class AlunoCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Aluno
    form_class = AlunoForm
    template_name = "core/aluno_form.html"
    success_url = reverse_lazy("aluno_list")

    def test_func(self):
        return self.request.user.is_staff


class AlunoUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Aluno
    form_class = AlunoForm
    template_name = "core/aluno_form.html"
    success_url = reverse_lazy("aluno_list")

    def test_func(self):
        return self.request.user.is_staff


class AlunoDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Aluno
    template_name = "core/confirm_delete.html"
    success_url = reverse_lazy("aluno_list")

    def test_func(self):
        return self.request.user.is_staff


# --- CRUD Professor ---
class ProfessorListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Professor
    template_name = "core/professor_list.html"
    context_object_name = "professores"

    def test_func(self):
        return self.request.user.is_staff


class ProfessorCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Professor
    form_class = ProfessorForm
    template_name = "core/professor_form.html"
    success_url = reverse_lazy("professor_list")

    def test_func(self):
        return self.request.user.is_staff


class ProfessorUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Professor
    form_class = ProfessorForm
    template_name = "core/professor_form.html"
    success_url = reverse_lazy("professor_list")

    def test_func(self):
        return self.request.user.is_staff


class ProfessorDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Professor
    template_name = "core/confirm_delete.html"
    success_url = reverse_lazy("professor_list")

    def test_func(self):
        return self.request.user.is_staff


# --- CRUD Banca ---
class BancaListView(LoginRequiredMixin, ListView):
    model = Banca
    template_name = "core/banca_list.html"
    context_object_name = "bancas"


class BancaDetailView(LoginRequiredMixin, DetailView):
    model = Banca
    template_name = "core/banca_detail.html"


class BancaCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Banca
    form_class = BancaForm
    template_name = "core/banca_form.html"
    success_url = reverse_lazy("banca_list")

    def test_func(self):
        """
        Permite o acesso apenas se o utilizador for admin ou o orientador/coorientador
        da monografia que está a ser agendada.
        """
        user = self.request.user
        if user.is_staff:
            return True

        monografia_id = self.request.GET.get("monografia")
        if not monografia_id:
            return False  # Nega o acesso se a URL for acedida sem o ID da monografia

        try:
            monografia = Monografia.objects.get(pk=monografia_id)
            if hasattr(user, "professor_profile"):
                professor_profile = user.professor_profile
                # Verifica se o professor logado é o orientador OU o coorientador
                return monografia.orientador == professor_profile or (
                    monografia.coorientador
                    and monografia.coorientador == professor_profile
                )
        except Monografia.DoesNotExist:
            return False

        return False

    def get_initial(self):
        initial = super().get_initial()
        monografia_id = self.request.GET.get("monografia")
        if monografia_id:
            initial["monografia"] = monografia_id
        return initial


class BancaUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Banca
    form_class = BancaForm
    template_name = "core/banca_form.html"
    success_url = reverse_lazy("banca_list")

    def test_func(self):
        """
        Permite a edição apenas se o utilizador for admin ou o orientador/coorientador
        da monografia associada à banca.
        """
        user = self.request.user
        if user.is_staff:
            return True

        # Apanha o objeto da banca e, a partir dele, a monografia
        banca = self.get_object()
        monografia = banca.monografia

        if hasattr(user, "professor_profile"):
            professor_profile = user.professor_profile
            # Verifica se o professor logado é o orientador OU o coorientador
            return monografia.orientador == professor_profile or (
                monografia.coorientador and monografia.coorientador == professor_profile
            )

        return False


class BancaDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Banca
    template_name = "core/confirm_delete.html"
    success_url = reverse_lazy("banca_list")

    def test_func(self):
        return is_professor(self.request.user) or self.request.user.is_staff


class HomePageView(TemplateView):
    template_name = "home.html"


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if hasattr(user, "aluno_profile"):
            context["user_type"] = "Aluno"
            try:
                context["monografia"] = Monografia.objects.get(aluno=user.aluno_profile)
            except Monografia.DoesNotExist:
                context["monografia"] = None
        elif hasattr(user, "professor_profile"):
            context["user_type"] = "Professor"
            context["monografias_orientadas"] = Monografia.objects.filter(
                orientador=user.professor_profile
            )
        else:
            context["user_type"] = "Usuário sem perfil definido"
        return context


class MonografiaHistoryView(LoginRequiredMixin, DetailView):
    model = Monografia
    template_name = "core/monografia_history.html"
    context_object_name = "monografia"

    def test_func(self):
        monografia = self.get_object()
        user = self.request.user

        if user.is_staff:
            return True

        if hasattr(user, "aluno_profile") and monografia.aluno == user.aluno_profile:
            return True

        if hasattr(user, "professor_profile"):
            professor_profile = user.professor_profile
            if monografia.orientador == professor_profile:
                return True
            if monografia.coorientador and monografia.coorientador == professor_profile:
                return True

        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["history_records"] = self.get_object().history.all()
        return context
