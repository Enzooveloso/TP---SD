from datetime import timedelta
from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Aluno, Banca, Monografia, Professor
from .validators import PasswordComplexityValidator


class BaseSetupMixin:
    def setUp(self):
        self.group_alunos, _ = Group.objects.get_or_create(name="Alunos")
        self.group_professores, _ = Group.objects.get_or_create(name="Professores")

        self.admin = User.objects.create_user(
            username="admin", email="admin@test.com", password="S3nha@Forte", is_staff=True
        )
        self.professor_user = User.objects.create_user(
            username="prof", email="prof@test.com", password="S3nha@Forte"
        )
        self.professor = Professor.objects.create(
            user=self.professor_user, titulacao=Professor.Titulacao.MESTRE, area_pesquisa="IA"
        )

        self.coorientador_user = User.objects.create_user(
            username="coor", email="coor@test.com", password="S3nha@Forte"
        )
        self.coorientador = Professor.objects.create(
            user=self.coorientador_user,
            titulacao=Professor.Titulacao.DOUTOR,
            area_pesquisa="Redes",
        )

        self.aluno_user = User.objects.create_user(
            username="aluno", email="aluno@test.com", password="S3nha@Forte"
        )
        self.aluno = Aluno.objects.create(user=self.aluno_user, matricula="2024001")

        self.sample_pdf = SimpleUploadedFile("teste.pdf", b"%PDF-1.4 teste")
        self.monografia = Monografia.objects.create(
            titulo="Estudo de Sistemas Distribuídos",
            resumo="Um resumo",
            abstract="Abstract content",
            palavras_chave="sistemas, distribuídos",
            arquivo_documento=self.sample_pdf,
            orientador=self.professor,
            coorientador=self.coorientador,
            aluno=self.aluno,
        )
        self.banca = Banca.objects.create(
            monografia=self.monografia,
            data_defesa=timezone.now() + timedelta(days=7),
            local_defesa="Auditório",
        )
        self.banca.avaliadores.add(self.professor)


class PasswordValidatorTests(TestCase):
    def test_password_complexity_validator(self):
        validator = PasswordComplexityValidator()
        with self.assertRaises(ValidationError):
            validator.validate("senhaFraca1")
        # Does not raise for strong password
        validator.validate("Senha@Fort3")


class MonografiaValidationTests(BaseSetupMixin, TestCase):
    def test_monografia_obrigatorio_coorientador_diferente(self):
        monografia = Monografia(
            titulo="Teste coorientador igual",
            resumo="Resumo",
            abstract="Abstract",
            palavras_chave="kw",
            orientador=self.professor,
            coorientador=self.professor,
            aluno=self.aluno,
        )
        with self.assertRaises(ValidationError):
            monografia.full_clean()


class MonografiaListViewTests(BaseSetupMixin, TestCase):
    def test_listagem_filtra_por_status_e_ordena(self):
        outra_monografia = Monografia.objects.create(
            titulo="Outro Trabalho",
            resumo="Resumo",
            abstract="Abstract",
            palavras_chave="ia",
            orientador=self.professor,
            coorientador=self.coorientador,
            aluno=self.aluno,
            status=Monografia.StatusMonografia.CONCLUIDA,
        )

        self.client.force_login(self.admin)
        response = self.client.get(
            reverse("monografia_list"),
            {"status": Monografia.StatusMonografia.CONCLUIDA, "ordenar": "titulo"},
        )
        self.assertEqual(response.status_code, 200)
        monografias = list(response.context["monografias"])
        self.assertEqual(monografias[0], outra_monografia)


class BancaPermissionsTests(BaseSetupMixin, TestCase):
    def test_professor_ve_apenas_bancas_relacionadas(self):
        outra_user = User.objects.create_user(
            username="prof2", email="prof2@test.com", password="S3nha@Forte"
        )
        outro_prof = Professor.objects.create(
            user=outra_user,
            titulacao=Professor.Titulacao.MESTRE,
            area_pesquisa="Dados",
        )
        outro_aluno_user = User.objects.create_user(
            username="aluno2", email="aluno2@test.com", password="S3nha@Forte"
        )
        outro_aluno = Aluno.objects.create(user=outro_aluno_user, matricula="2024002")
        outra_monografia = Monografia.objects.create(
            titulo="Outro Tema",
            resumo="Resumo",
            abstract="Abstract",
            palavras_chave="dados",
            orientador=outro_prof,
            coorientador=self.coorientador,
            aluno=outro_aluno,
        )
        outra_banca = Banca.objects.create(
            monografia=outra_monografia,
            data_defesa=timezone.now() + timedelta(days=10),
            local_defesa="Sala 2",
        )
        outra_banca.avaliadores.add(outro_prof)

        self.client.force_login(self.professor_user)
        response = self.client.get(reverse("banca_list"))
        self.assertEqual(response.status_code, 200)
        bancas = list(response.context["bancas"])
        self.assertIn(self.banca, bancas)
        self.assertNotIn(outra_banca, bancas)
