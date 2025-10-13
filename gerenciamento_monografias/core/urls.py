from django.urls import path, include
from .views import (
    AlunoListView, AlunoCreateView, AlunoUpdateView, AlunoDeleteView,
    ProfessorListView, ProfessorCreateView, ProfessorUpdateView, ProfessorDeleteView,
    MonografiaListView, MonografiaDetailView, MonografiaCreateView, MonografiaUpdateView, MonografiaDeleteView,
    BancaListView, BancaDetailView, BancaCreateView, BancaUpdateView, BancaDeleteView, HomePageView, DashboardView, MonografiaHistoryView
)

# URLs de Aluno
aluno_patterns = [
    path('', AlunoListView.as_view(), name='aluno_list'),
    path('new/', AlunoCreateView.as_view(), name='aluno_new'),
    path('<int:pk>/edit/', AlunoUpdateView.as_view(), name='aluno_edit'),
    path('<int:pk>/delete/', AlunoDeleteView.as_view(), name='aluno_delete'),
]

# URLs de Professor
professor_patterns = [
    path('', ProfessorListView.as_view(), name='professor_list'),
    path('new/', ProfessorCreateView.as_view(), name='professor_new'),
    path('<int:pk>/edit/', ProfessorUpdateView.as_view(), name='professor_edit'),
    path('<int:pk>/delete/', ProfessorDeleteView.as_view(), name='professor_delete'),
]

# URLs de Monografia
monografia_patterns = [
    path('', MonografiaListView.as_view(), name='monografia_list'),
    path('<int:pk>/', MonografiaDetailView.as_view(), name='monografia_detail'),
    path('new/', MonografiaCreateView.as_view(), name='monografia_new'),
    path('<int:pk>/edit/', MonografiaUpdateView.as_view(), name='monografia_edit'),
    path('<int:pk>/delete/', MonografiaDeleteView.as_view(), name='monografia_delete'),
    path('<int:pk>/history/', MonografiaHistoryView.as_view(), name='monografia_history'),
]

# URLs de Banca
banca_patterns = [
    path('', BancaListView.as_view(), name='banca_list'),
    path('<int:pk>/', BancaDetailView.as_view(), name='banca_detail'),
    path('new/', BancaCreateView.as_view(), name='banca_new'),
    path('<int:pk>/edit/', BancaUpdateView.as_view(), name='banca_edit'),
    path('<int:pk>/delete/', BancaDeleteView.as_view(), name='banca_delete'),
]


urlpatterns = [
    path('alunos/', include(aluno_patterns)),
    path('professores/', include(professor_patterns)),
    path('monografias/', include(monografia_patterns)),
    path('bancas/', include(banca_patterns)),
    path('', HomePageView.as_view(), name='home'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]