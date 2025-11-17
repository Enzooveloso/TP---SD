import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from faker import Faker

from core.models import Aluno, Banca, Monografia, Professor

User = get_user_model()


class Command(BaseCommand):
    help = "Popula o banco com dados de exemplo (professores, alunos, monografias e bancas)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=10,
            help="Quantidade de monografias/alunos a serem criados (professores são gerados proporcionalmente).",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Remove dados existentes antes de popular novamente.",
        )
        parser.add_argument(
            "--fake",
            action="store_true",
            help="Executa todo o processo sem gravar nada (dry-run).",
        )

    def handle(self, *args, **options):
        self.faker = Faker("pt_BR")
        self.fake_run = options["fake"]
        count = max(1, options["count"])

        if options["clear"]:
            self.clear_data()

        # Garante que grupos base existam
        self.group_alunos, _ = Group.objects.get_or_create(name="Alunos")
        self.group_professores, _ = Group.objects.get_or_create(name="Professores")

        with transaction.atomic():
            professores = self.seed_professores(max(5, count // 2 + 2))
            self.stdout.write(self.style.SUCCESS("Populando Professores: OK"))

            alunos = self.seed_alunos(count)
            self.stdout.write(self.style.SUCCESS("Populando Alunos: OK"))

            monografias = self.seed_monografias(alunos, professores)
            self.stdout.write(self.style.SUCCESS("Populando Monografias: OK"))

            defesas = self.seed_defesas(monografias)

            bancas = self.seed_banca(monografias, professores, defesas)
            self.stdout.write(self.style.SUCCESS("Populando Bancas: OK"))

            self.seed_historico(monografias, professores)
            self.stdout.write(self.style.SUCCESS("Populando Histórico: OK"))

            if self.fake_run:
                transaction.set_rollback(True)
                self.stdout.write(
                    self.style.WARNING("Modo --fake ativo: nenhuma alteração foi persistida.")
                )
                return

        self.stdout.write(self.style.SUCCESS("Banco populado com sucesso!"))

    def clear_data(self):
        """Remove dados das tabelas principais e arquivos associados."""
        self.stdout.write("Limpando dados existentes...")

        Banca.objects.all().delete()

        # Remove arquivos de monografias antes de apagar os registros
        for monografia in Monografia.objects.all():
            if monografia.arquivo_documento:
                monografia.arquivo_documento.delete(save=False)
        Monografia.history.model.objects.all().delete()
        Monografia.objects.all().delete()

        Aluno.objects.all().delete()
        Professor.objects.all().delete()

        # Mantém superusuários; remove demais usuários criados para perfis
        User.objects.filter(is_superuser=False, is_staff=False).delete()

    def seed_professores(self, quantidade):
        titulacoes = list(Professor.Titulacao.values)
        areas = [
            "Inteligência Artificial",
            "Redes de Computadores",
            "Banco de Dados",
            "Engenharia de Software",
            "Segurança da Informação",
            "Computação em Nuvem",
            "Ciência de Dados",
            "Desenvolvimento Web",
            "Arquitetura de Sistemas",
            "Computação Gráfica",
        ]

        professores = []
        for _ in range(quantidade):
            nome = self.faker.name()
            first_name, *last_parts = nome.split(" ")
            last_name = " ".join(last_parts) if last_parts else ""

            username = self.unique_username()
            email = f"{first_name.lower()}.{last_parts[0].lower() if last_parts else username}@ufvjm.edu.br"

            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password="Senha@1234",
            )
            user.groups.add(self.group_professores)

            professor = Professor.objects.create(
                user=user,
                titulacao=random.choice(titulacoes),
                area_pesquisa=random.choice(areas),
            )
            professores.append(professor)
        return professores

    def seed_alunos(self, quantidade):
        alunos = []
        for _ in range(quantidade):
            nome = self.faker.name()
            first_name, *last_parts = nome.split(" ")
            last_name = " ".join(last_parts) if last_parts else ""
            username = self.unique_username()
            email = f"{first_name.lower()}.{last_parts[0].lower() if last_parts else username}@aluno.ufvjm.edu.br"

            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password="Senha@1234",
            )
            user.groups.add(self.group_alunos)

            matricula = self.faker.unique.random_number(digits=8, fix_len=True)
            alunos.append(Aluno.objects.create(user=user, matricula=str(matricula)))
        return alunos

    def seed_monografias(self, alunos, professores):
        keywords_pool = [
            "machine learning",
            "deep learning",
            "cloud computing",
            "microservices",
            "banco de dados",
            "internet das coisas",
            "segurança",
            "engenharia de software",
            "devops",
            "computação móvel",
            "blockchain",
            "sistemas distribuídos",
            "big data",
            "processamento de linguagem natural",
        ]

        monografias = []
        status_choices = [
            Monografia.StatusMonografia.EM_ANDAMENTO,
            Monografia.StatusMonografia.CONCLUIDA,
            Monografia.StatusMonografia.APROVADA,
            Monografia.StatusMonografia.REPROVADA,
        ]

        for aluno in alunos:
            try:
                existing = aluno.monografia
            except Monografia.DoesNotExist:
                existing = None

            if existing:
                monografias.append(existing)
                continue

            orientador = random.choice(professores)
            coorientaveis = [prof for prof in professores if prof.id != orientador.id]
            coorientador = random.choice(coorientaveis) if coorientaveis and random.random() > 0.4 else None

            titulo = self.faker.sentence(nb_words=6).rstrip(".")
            resumo = self.faker.paragraph(nb_sentences=5)
            abstract = self.faker.paragraph(nb_sentences=5)
            palavras = ", ".join(random.sample(keywords_pool, k=3))
            status = random.choice(status_choices)

            monografia = Monografia.objects.create(
                titulo=titulo,
                resumo=resumo,
                abstract=abstract,
                palavras_chave=palavras,
                orientador=orientador,
                coorientador=coorientador,
                aluno=aluno,
                status=status,
            )

            if random.random() > 0.2:
                pdf_content = self.fake_pdf(monografia)
                monografia.arquivo_documento.save(pdf_content.name, pdf_content, save=True)

            monografias.append(monografia)

        return monografias

    def seed_defesas(self, monografias):
        """
        Define datas de defesa coerentes para cada monografia (passadas ou futuras) e retorna um mapa para uso na banca.
        """
        defesas = {}
        now = timezone.now()
        for monografia in monografias:
            if monografia.status == Monografia.StatusMonografia.EM_ANDAMENTO:
                dt = self.faker.date_time_between(start_date="+10d", end_date="+240d")
            elif monografia.status == Monografia.StatusMonografia.CONCLUIDA:
                dt = self.faker.date_time_between(start_date="-90d", end_date="+90d")
            else:
                dt = self.faker.date_time_between(start_date="-5y", end_date="-10d")

            dt = timezone.make_aware(dt) if timezone.is_naive(dt) else dt
            if dt < now - timedelta(days=5 * 365):
                dt = now - timedelta(days=30)

            monografia.data_defesa = dt.date()
            monografia.save(update_fields=["data_defesa"])
            defesas[monografia.id] = dt
        return defesas

    def seed_banca(self, monografias, professores, defesas):
        bancas = []
        locais = [
            "Auditório Central",
            "Sala de Reuniões 1",
            "Laboratório de Redes",
            "Laboratório de IA",
            "Auditório Norte",
            "Sala 204 - Bloco Tecnológico",
        ]

        for monografia in monografias:
            avaliadores = random.sample(
                professores, k=min(3, len(professores))
            ) or [random.choice(professores)]

            try:
                existing_banca = monografia.banca
                bancas.append(existing_banca)
                continue
            except Banca.DoesNotExist:
                existing_banca = None

            nota_final = None
            if monografia.status in (
                Monografia.StatusMonografia.APROVADA,
                Monografia.StatusMonografia.CONCLUIDA,
            ):
                nota_final = round(random.uniform(70, 100), 2)
            elif monografia.status == Monografia.StatusMonografia.REPROVADA:
                nota_final = round(random.uniform(50, 69), 2)

            banca = Banca.objects.create(
                monografia=monografia,
                data_defesa=defesas.get(monografia.id, timezone.now() + timedelta(days=30)),
                local_defesa=random.choice(locais),
                nota_final=Decimal(nota_final) if nota_final else None,
            )
            banca.avaliadores.set(avaliadores)
            bancas.append(banca)
        return bancas

    def seed_historico(self, monografias, professores):
        """
        Cria registros adicionais no histórico de cada monografia simulando alterações reais.
        """
        for monografia in monografias:
            eventos = random.randint(1, 3)
            for _ in range(eventos):
                monografia.resumo = self.faker.paragraph(nb_sentences=4)
                monografia.abstract = self.faker.paragraph(nb_sentences=4)
                monografia.status = random.choice(
                    [
                        Monografia.StatusMonografia.EM_ANDAMENTO,
                        Monografia.StatusMonografia.CONCLUIDA,
                        Monografia.StatusMonografia.APROVADA,
                        Monografia.StatusMonografia.REPROVADA,
                    ]
                )
                monografia._history_user = random.choice(professores).user
                monografia.save()

    def fake_pdf(self, monografia):
        """
        Gera um pequeno PDF fictício para anexar à monografia.
        """
        content = f"%PDF-1.4\n%Fake PDF para {monografia.titulo}\nMonografia do aluno {monografia.aluno.user.get_full_name()}.\nPalavras-chave: {monografia.palavras_chave}\n%%EOF"
        file_name = f"monografia_{monografia.aluno.matricula}.pdf"
        return ContentFile(content.encode("utf-8"), name=file_name)

    def unique_username(self):
        """Garante que o username seja único no banco para evitar colisões entre execuções."""
        username = self.faker.unique.user_name()
        while User.objects.filter(username=username).exists():
            username = self.faker.unique.user_name()
        return username
