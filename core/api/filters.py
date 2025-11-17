import django_filters
from core.models import Monografia


class MonografiaFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name="status")
    orientador = django_filters.NumberFilter(field_name="orientador_id")
    area_pesquisa = django_filters.CharFilter(field_name="orientador__area_pesquisa", lookup_expr="icontains")
    ano_publicacao = django_filters.NumberFilter(field_name="data_publicacao__year")

    class Meta:
        model = Monografia
        fields = ["status", "orientador", "area_pesquisa", "ano_publicacao"]
