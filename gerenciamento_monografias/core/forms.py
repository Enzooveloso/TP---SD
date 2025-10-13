from django import forms
from .models import Aluno, Banca, Monografia, Professor
from django.contrib.auth.models import User, Group

class MonografiaForm(forms.ModelForm):
    class Meta:
        model = Monografia
        fields = [
            'titulo', 'resumo', 'abstract', 'palavras_chave', 'status',
            'aluno', 'orientador', 'coorientador', 'arquivo_documento'
        ]

        # Opcional: Adicionar widgets para melhorar a interface,
        # por exemplo, usando um select mais amigável ou caixas de texto maiores.
        widgets = {
            'data_publicacao': forms.DateInput(attrs={'type': 'date'}),
        }
    def clean(self):
        # Pega todos os dados já validados do formulário
        cleaned_data = super().clean()
        orientador = cleaned_data.get("orientador")
        coorientador = cleaned_data.get("coorientador")

            # Nossa regra de negócio
        if orientador and coorientador and orientador == coorientador:
                # Se a regra for violada 
            raise forms.ValidationError(
                "O orientador e o coorientador não podem ser a mesma pessoa."
            )
        return cleaned_data     

class BancaForm(forms.ModelForm):
    class Meta:
        model = Banca
        fields = ['monografia', 'avaliadores', 'data_defesa', 'local_defesa', 'nota_final']
        widgets = {
            'data_defesa': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'avaliadores': forms.CheckboxSelectMultiple,
        }

class AlunoForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(aluno_profile__isnull=True),
        label="Usuário"
    )
    class Meta:
        model = Aluno
        
        fields = ['user', 'matricula']


class ProfessorForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(professor_profile__isnull=True),
        label="Usuário"
    )

    class Meta:
        model = Professor
        fields = ['user', 'titulacao', 'area_pesquisa']

class CustomSignupForm(forms.Form):
    """
    Este formulário estende o formulário de registro padrão do allauth
    para incluir um campo de seleção de tipo de usuário.
    """
    user_type = forms.ChoiceField(
        choices=[('aluno', 'Sou Aluno'), ('professor', 'Sou Professor')],
        label="Eu sou",
        required=True
    )

    def signup(self, request, user):
        """
        Esta função é chamada após o usuário preencher o formulário
        e o usuário base (com username/email/senha) já ter sido criado.
        """
        user_type = self.cleaned_data['user_type']
        

        if user_type == 'aluno':
            group = Group.objects.get(name='Alunos')
        elif user_type == 'professor':
            group = Group.objects.get(name='Professores')

        user.groups.add(group)

        user.save()