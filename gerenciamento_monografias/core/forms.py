from django import forms
from .models import Aluno, Banca, Monografia, Professor

class MonografiaForm(forms.ModelForm):
    class Meta:
        model = Monografia
        fields = [
            'titulo', 'resumo', 'abstract', 'palavras_chave', 'status',
            'aluno', 'orientador', 'coorientador'
        ]

        # Opcional: Adicionar widgets para melhorar a interface,
        # por exemplo, usando um select mais amigável ou caixas de texto maiores.
        widgets = {
            'data_publicacao': forms.DateInput(attrs={'type': 'date'}),
        }

class BancaForm(forms.ModelForm):
    class Meta:
        model = Banca
        fields = ['monografia', 'avaliadores', 'data_defesa', 'local_defesa', 'nota_final']
        widgets = {
            'data_defesa': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            # Renderiza ManyToManyField como uma caixa de seleção múltipla por padrão.
            # Um widget de Checkbox.
            'avaliadores': forms.CheckboxSelectMultiple,
        }

class AlunoForm(forms.ModelForm):
    class Meta:
        model = Aluno
        fields = [
            'nome',
            'matricula',
            'email',
        ]

class ProfessorForm(forms.ModelForm):
    class Meta:
        model = Professor
        fields = [
            'nome',
            'email',
            'titulacao',
            'area_pesquisa',
        ]