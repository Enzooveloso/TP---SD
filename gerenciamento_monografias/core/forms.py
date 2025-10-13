from django import forms
from .models import Aluno, Banca, Monografia, Professor
from django.contrib.auth.models import User, Group

class MonografiaForm(forms.ModelForm):
    class Meta:
        model = Monografia
        fields = [
            'titulo', 'resumo', 'abstract', 'palavras_chave', 'status', 'orientador', 'coorientador', 'arquivo_documento'
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

    def clean_nota_final(self):
        """
        Valida se a nota final está dentro do limite permitido (0 a 100).
        """
        nota = self.cleaned_data.get('nota_final')

        # 'nota is not None' garante que a validação só rode se o campo for preenchido.
        if nota is not None:
            if nota > 100:
                raise forms.ValidationError("A nota final não pode ser maior que 100.")
            if nota < 0:
                raise forms.ValidationError("A nota final не pode ser negativa.")
        
        return nota # Sempre retorne o valor limpo no final.

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
    user_type = forms.ChoiceField(
        choices=[('', '---------'), ('aluno', 'Sou Aluno'), ('professor', 'Sou Professor')],
        label="Eu sou",
        required=True
    )
    
    # Campo para o Aluno
    matricula = forms.CharField(
        max_length=20,
        label="Matrícula",
        required=False  # A obrigatoriedade será validada no método clean()
    )

    # Campos para o Professor
    titulacao = forms.ChoiceField(
        choices=Professor.Titulacao.choices,
        label="Titulação",
        required=False
    )
    area_pesquisa = forms.CharField(
        max_length=255,
        label="Área de Pesquisa",
        required=False
    )

    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')

        if user_type == 'aluno':
            matricula = cleaned_data.get('matricula')
            if not matricula:
                self.add_error('matricula', 'Este campo é obrigatório para alunos.')

        elif user_type == 'professor':
            titulacao = cleaned_data.get('titulacao')
            area_pesquisa = cleaned_data.get('area_pesquisa')
            if not titulacao:
                self.add_error('titulacao', 'Este campo é obrigatório para professores.')
            if not area_pesquisa:
                self.add_error('area_pesquisa', 'Este campo é obrigatório para professores.')
        
        return cleaned_data

    def signup(self, request, user):
        user.save() 
        user_type = self.cleaned_data['user_type']
        
        if user_type == 'aluno':
            group = Group.objects.get(name='Alunos')
            user.groups.add(group)
            Aluno.objects.create(
                user=user,
                matricula=self.cleaned_data['matricula']
            )
            
        elif user_type == 'professor':
            group = Group.objects.get(name='Professores')
            user.groups.add(group)

            Professor.objects.create(
                user=user,
                titulacao=self.cleaned_data['titulacao'],
                area_pesquisa=self.cleaned_data['area_pesquisa']
            )