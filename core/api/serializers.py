from rest_framework import serializers
from core.models import Monografia, Professor, Banca


class ProfessorSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(source="user.get_full_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Professor
        fields = ["id", "nome", "email", "titulacao", "area_pesquisa"]


class BancaSerializer(serializers.ModelSerializer):
    avaliadores = ProfessorSerializer(many=True, read_only=True)
    avaliadores_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Professor.objects.all(),
        source="avaliadores",
        required=False,
    )

    class Meta:
        model = Banca
        fields = [
            "id",
            "monografia",
            "avaliadores",
            "avaliadores_ids",
            "data_defesa",
            "local_defesa",
            "nota_final",
        ]
        read_only_fields = []


class MonografiaSerializer(serializers.ModelSerializer):
    orientador_nome = serializers.CharField(source="orientador.user.get_full_name", read_only=True)
    coorientador_nome = serializers.CharField(source="coorientador.user.get_full_name", read_only=True)
    aluno_nome = serializers.CharField(source="aluno.user.get_full_name", read_only=True)
    banca = BancaSerializer(read_only=True)
    arquivo_url = serializers.SerializerMethodField()

    class Meta:
        model = Monografia
        fields = [
            "id",
            "titulo",
            "resumo",
            "abstract",
            "palavras_chave",
            "status",
            "data_publicacao",
            "data_defesa",
            "orientador",
            "coorientador",
            "orientador_nome",
            "coorientador_nome",
            "aluno",
            "aluno_nome",
            "arquivo_documento",
            "arquivo_url",
            "banca",
        ]
        read_only_fields = ["data_publicacao"]

    def get_arquivo_url(self, obj):
        request = self.context.get("request")
        if obj.arquivo_documento and request:
            return request.build_absolute_uri(obj.arquivo_documento.url)
        return None

    def validate(self, attrs):
        orientador = attrs.get("orientador") or getattr(self.instance, "orientador", None)
        coorientador = attrs.get("coorientador") or getattr(self.instance, "coorientador", None)
        if orientador and coorientador and orientador == coorientador:
            raise serializers.ValidationError("Orientador e coorientador devem ser diferentes.")
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        if hasattr(user, "aluno_profile"):
            validated_data["aluno"] = user.aluno_profile
        elif "aluno" not in validated_data:
            raise serializers.ValidationError("Campo aluno é obrigatório para administradores.")
        return super().create(validated_data)
