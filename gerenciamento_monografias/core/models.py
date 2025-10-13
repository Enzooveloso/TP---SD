from django.db import models
from django.conf import settings  # Para referenciar o modelo User padrão
from simple_history.models import HistoricalRecords  # Import para histórico de mudanças


# Modelo para o perfil de Professor (servirá para Orientador, Coorientador e Avaliadores)
class Professor(models.Model):
    # Classe interna para as opções de titulação
    class Titulacao(models.TextChoices):
        MESTRE = "ME", "Mestre"
        DOUTOR = "DR", "Doutor"
        POS_DOUTOR = "PD", "Pós-Doutor"

    # Relação um-para-um com o usuário padrão do Django. Cada usuário só pode ter um perfil de professor.
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="professor_profile",
    )

    # Campos específicos do professor
    titulacao = models.CharField(
        max_length=2, choices=Titulacao.choices, verbose_name="Titulação"
    )
    area_pesquisa = models.CharField(max_length=255, verbose_name="Área de Pesquisa")

    def __str__(self):
        # Retorna o nome completo do usuário associado para uma melhor representação no admin
        return self.user.get_full_name() or self.user.username

    class Meta:
        verbose_name = "Professor"
        verbose_name_plural = "Professores"


# Modelo para o perfil de Aluno
class Aluno(models.Model):
    # Relação um-para-um com o usuário padrão do Django.
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="aluno_profile"
    )

    # Campo específico do aluno
    matricula = models.CharField(max_length=20, unique=True, verbose_name="Matrícula")

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    class Meta:
        verbose_name = "Aluno"
        verbose_name_plural = "Alunos"


# Modelo central: a Monografia
class Monografia(models.Model):
    # Classe interna para as opções de status
    class StatusMonografia(models.TextChoices):
        EM_ANDAMENTO = "AND", "Em Andamento"
        CONCLUIDA = "CON", "Concluída para Defesa"
        APROVADA = "APR", "Aprovada"
        REPROVADA = "REP", "Reprovada"

    titulo = models.CharField(max_length=255, verbose_name="Título")
    resumo = models.TextField()
    abstract = models.TextField()
    palavras_chave = models.CharField(
        max_length=255, verbose_name="Palavras-Chave", help_text="Separadas por vírgula"
    )
    history = HistoricalRecords() # para ter histórico de mudanças
    # Campo para o upload do arquivo da monografia
    arquivo_documento = models.FileField(
        upload_to='monografias/', # Subpasta dentro do diretório de mídia
        blank=True, # permite que o campo fique em branco
        null=True,  # permite que o valor no banco de dados seja nulo
        verbose_name="Documento (PDF)"
    )

    status = models.CharField(
        max_length=3,
        choices=StatusMonografia.choices,
        default=StatusMonografia.EM_ANDAMENTO,
    )
    data_publicacao = models.DateField(
        auto_now_add=True, verbose_name="Data de Publicação"
    )

    # Relacionamentos
    aluno = models.OneToOneField(
        Aluno, on_delete=models.CASCADE, related_name="monografia"
    )
    orientador = models.ForeignKey(
        Professor,
        on_delete=models.SET_NULL,
        null=True,
        related_name="monografias_orientadas",
    )
    coorientador = models.ForeignKey(
        Professor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="monografias_coorientadas",
    )

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = "Monografia"
        verbose_name_plural = "Monografias"
        permissions = [
            ("can_delete_monografia", "Pode deletar monografia"),
        ]


# Modelo para a Banca Examinadora
class Banca(models.Model):
    # Relação um-para-um com a Monografia. Cada monografia tem apenas uma banca.
    monografia = models.OneToOneField(
        Monografia, on_delete=models.CASCADE, related_name="banca"
    )

    # Relação muitos-para-muitos com Professores. A banca é composta por vários professores.
    avaliadores = models.ManyToManyField(Professor, related_name="bancas_avaliadas")

    data_defesa = models.DateTimeField(verbose_name="Data e Hora da Defesa")
    local_defesa = models.CharField(max_length=255, verbose_name="Local da Defesa")

    # Usamos DecimalField para precisão na nota.
    nota_final = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="Nota Final"
    )

    def __str__(self):
        return f"Banca da monografia: {self.monografia.titulo}"

    class Meta:
        verbose_name = "Banca"
        verbose_name_plural = "Bancas"
