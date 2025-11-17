from django import forms
from .models import Aluno, Banca, Monografia, Professor
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError


PDF_HELP = "Envie um PDF de até 10MB."


class MonografiaForm(forms.ModelForm):
    class Meta:
        model = Monografia
        fields = [
            "titulo",
            "resumo",
            "abstract",
            "palavras_chave",
            "data_defesa",
            "status",
            "orientador",
            "coorientador",
            "arquivo_documento",
        ]

        # Opcional: Adicionar widgets para melhorar a interface,
        # por exemplo, usando um select mais amigável ou caixas de texto maiores.
        widgets = {
            "data_publicacao": forms.DateInput(attrs={"type": "date"}),
            "data_defesa": forms.DateInput(attrs={"type": "date"}),
            "resumo": forms.Textarea(attrs={"rows": 4}),
            "abstract": forms.Textarea(attrs={"rows": 4}),
            "palavras_chave": forms.TextInput(
                attrs={"placeholder": "ex: inteligência artificial, redes neurais"}
            ),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        professor_qs = Professor.objects.select_related("user").all()
        self.fields["orientador"].queryset = professor_qs
        self.fields["coorientador"].queryset = professor_qs
        self.fields["arquivo_documento"].help_text = PDF_HELP
        self.fields["arquivo_documento"].required = self.instance.pk is None
        self.fields["coorientador"].required = True

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

    def clean_arquivo_documento(self):
        arquivo = self.cleaned_data.get("arquivo_documento")
        if arquivo and arquivo.size > 10 * 1024 * 1024:
            raise ValidationError("O arquivo não pode ultrapassar 10MB.")
        return arquivo


class BancaForm(forms.ModelForm):
    class Meta:
        model = Banca
        fields = [
            "monografia",
            "avaliadores",
            "data_defesa",
            "local_defesa",
            "nota_final",
        ]
        widgets = {
            "data_defesa": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "avaliadores": forms.CheckboxSelectMultiple(),
        }

    def clean_nota_final(self):
        """
        Valida se a nota final está dentro do limite permitido (0 a 100).
        """
        nota = self.cleaned_data.get("nota_final")

        # 'nota is not None' garante que a validação só rode se o campo for preenchido.
        if nota is not None:
            if nota > 100:
                raise forms.ValidationError("A nota final não pode ser maior que 100.")
            if nota < 0:
                raise forms.ValidationError("A nota final não pode ser negativa.")

        return nota  # Sempre retorne o valor limpo no final.

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Evita criar múltiplas bancas para a mesma monografia quando criando uma nova.
        if not self.instance.pk:
            self.fields["monografia"].queryset = Monografia.objects.filter(
                banca__isnull=True
            )
        self.fields["avaliadores"].queryset = Professor.objects.select_related("user")


class AlunoForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(aluno_profile__isnull=True), label="Usuário"
    )

    class Meta:
        model = Aluno

        fields = ["user", "matricula"]


class ProfessorForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(professor_profile__isnull=True), label="Usuário"
    )

    class Meta:
        model = Professor
        fields = ["user", "titulacao", "area_pesquisa"]


class CustomSignupForm(forms.Form):
    user_type = forms.ChoiceField(
        choices=[
            ("", "---------"),
            ("aluno", "Sou Aluno"),
            ("professor", "Sou Professor"),
        ],
        label="Eu sou",
        required=True,
    )

    # Campo para o Aluno
    matricula = forms.CharField(
        max_length=20,
        label="Matrícula",
        required=False,  # A obrigatoriedade será validada no método clean()
    )

    # Campos para o Professor
    titulacao = forms.ChoiceField(
        choices=Professor.Titulacao.choices, label="Titulação", required=False
    )
    area_pesquisa = forms.CharField(
        max_length=255, label="Área de Pesquisa", required=False
    )

    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get("user_type")

        if user_type == "aluno":
            matricula = cleaned_data.get("matricula")
            if not matricula:
                self.add_error("matricula", "Este campo é obrigatório para alunos.")

        elif user_type == "professor":
            titulacao = cleaned_data.get("titulacao")
            area_pesquisa = cleaned_data.get("area_pesquisa")
            if not titulacao:
                self.add_error(
                    "titulacao", "Este campo é obrigatório para professores."
                )
            if not area_pesquisa:
                self.add_error(
                    "area_pesquisa", "Este campo é obrigatório para professores."
                )

        return cleaned_data

    def signup(self, request, user):
        user.save()
        user_type = self.cleaned_data["user_type"]

        if user_type == "aluno":
            group, _ = Group.objects.get_or_create(name="Alunos")
            user.groups.add(group)
            Aluno.objects.create(user=user, matricula=self.cleaned_data["matricula"])

        elif user_type == "professor":
            group, _ = Group.objects.get_or_create(name="Professores")
            user.groups.add(group)

            Professor.objects.create(
                user=user,
                titulacao=self.cleaned_data["titulacao"],
                area_pesquisa=self.cleaned_data["area_pesquisa"],
            )
