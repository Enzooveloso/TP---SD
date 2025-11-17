from django.urls import path, include
from rest_framework import routers

from core.api.views import (
    MonografiaPublicViewSet,
    ProfessorPublicViewSet,
    MonografiaViewSet,
    BancaViewSet,
    MonografiasPorAnoView,
    MonografiasPorAreaView,
    MonografiasPorStatusView,
)

router = routers.DefaultRouter()
router.register(r"public/monografias", MonografiaPublicViewSet, basename="public-monografias")
router.register(r"public/professores", ProfessorPublicViewSet, basename="public-professores")
router.register(r"monografias", MonografiaViewSet, basename="api-monografias")
router.register(r"bancas", BancaViewSet, basename="api-bancas")

urlpatterns = [
    path("", include(router.urls)),
    path("stats/monografias_por_ano/", MonografiasPorAnoView.as_view(), name="stats-monografias-ano"),
    path("stats/monografias_por_area/", MonografiasPorAreaView.as_view(), name="stats-monografias-area"),
    path("stats/monografias_por_status/", MonografiasPorStatusView.as_view(), name="stats-monografias-status"),
]
