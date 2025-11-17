from django.db.models import Count, F
from django.http import HttpResponse
from rest_framework import viewsets, permissions, status, exceptions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Monografia, Professor, Banca
from core.api.serializers import (
    MonografiaSerializer,
    ProfessorSerializer,
    BancaSerializer,
)
from core.api.permissions import IsAlunoOwnerOrOrientador, IsProfessorOrAdminBanca
from core.api.filters import MonografiaFilter
from core.utils.pdf import gerar_ata_defesa_pdf


class MonografiaPublicViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Monografia.objects.filter(
        status=Monografia.StatusMonografia.APROVADA
    ).select_related("orientador__user", "coorientador__user", "aluno__user")
    serializer_class = MonografiaSerializer
    permission_classes = [permissions.AllowAny]
    filterset_class = MonografiaFilter
    search_fields = ["titulo", "resumo", "abstract", "palavras_chave"]
    ordering_fields = ["data_publicacao", "titulo"]
    ordering = ["-data_publicacao"]


class ProfessorPublicViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Professor.objects.select_related("user")
    serializer_class = ProfessorSerializer
    permission_classes = [permissions.AllowAny]
    search_fields = ["user__first_name", "user__last_name", "area_pesquisa"]
    ordering_fields = ["user__first_name", "user__last_name", "area_pesquisa"]


class MonografiaViewSet(viewsets.ModelViewSet):
    queryset = Monografia.objects.select_related(
        "orientador__user", "coorientador__user", "aluno__user"
    )
    serializer_class = MonografiaSerializer
    filterset_class = MonografiaFilter
    search_fields = ["titulo", "resumo", "abstract", "palavras_chave"]
    ordering_fields = ["data_publicacao", "titulo", "status", "data_defesa"]
    permission_classes = [permissions.IsAuthenticated, IsAlunoOwnerOrOrientador]

    def create(self, request, *args, **kwargs):
        user = request.user
        if not (user.is_staff or hasattr(user, "aluno_profile")):
            return Response(
                {"detail": "Apenas alunos ou administradores podem criar monografia."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

    @action(detail=True, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def historico(self, request, pk=None):
        monografia = self.get_object()
        history = [
            {
                "data": h.history_date,
                "usuario": str(h.history_user) if h.history_user else None,
                "tipo": h.get_history_type_display(),
            }
            for h in monografia.history.all()
        ]
        return Response(history)


class BancaViewSet(viewsets.ModelViewSet):
    queryset = Banca.objects.select_related(
        "monografia__aluno__user",
        "monografia__orientador__user",
        "monografia__coorientador__user",
    ).prefetch_related("avaliadores__user")
    serializer_class = BancaSerializer
    permission_classes = [permissions.IsAuthenticated, IsProfessorOrAdminBanca]
    filterset_fields = ["data_defesa"]
    ordering_fields = ["data_defesa"]

    def perform_create(self, serializer):
        monografia_id = self.request.data.get("monografia")
        monografia = Monografia.objects.get(pk=monografia_id)
        user = self.request.user
        if not user.is_staff:
            if not hasattr(user, "professor_profile"):
                raise exceptions.PermissionDenied("Apenas orientadores ou admin podem agendar.")
            prof = user.professor_profile
            if not (monografia.orientador == prof or monografia.coorientador == prof):
                raise exceptions.PermissionDenied("Somente orientador ou coorientador podem agendar a banca.")
        if hasattr(monografia, "banca"):
            raise exceptions.PermissionDenied("Esta monografia já possui banca.")
        serializer.save(monografia=monografia)
        if monografia.data_defesa != serializer.validated_data.get("data_defesa").date():
            monografia.data_defesa = serializer.validated_data.get("data_defesa").date()
            monografia.save(update_fields=["data_defesa"])

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated, IsProfessorOrAdminBanca])
    def registrar_nota(self, request, pk=None):
        banca = self.get_object()
        nota = request.data.get("nota_final")
        if nota is None:
            return Response({"detail": "nota_final é obrigatória"}, status=status.HTTP_400_BAD_REQUEST)
        banca.nota_final = nota
        banca.save(update_fields=["nota_final"])
        return Response(self.get_serializer(banca).data)

    @action(detail=True, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def ata(self, request, pk=None):
        banca = self.get_object()
        pdf_bytes = gerar_ata_defesa_pdf(banca)
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="ata_{banca.pk}.pdf"'
        return response


class MonografiasPorAnoView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        data = (
            Monografia.objects.values(ano=F("data_publicacao__year"))
            .annotate(total=Count("id"))
            .order_by("ano")
        )
        return Response(list(data))


class MonografiasPorAreaView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        data = (
            Monografia.objects.values(area=F("orientador__area_pesquisa"))
            .annotate(total=Count("id"))
            .order_by("area")
        )
        return Response(list(data))


class MonografiasPorStatusView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        data = (
            Monografia.objects.values("status")
            .annotate(total=Count("id"))
            .order_by("status")
        )
        return Response(list(data))
