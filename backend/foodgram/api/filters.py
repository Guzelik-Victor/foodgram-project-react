from django_filters import rest_framework
from recipes.models import Recipe


class TitleFilters(rest_framework.FilterSet):
    """Генериция фильтров для указанных полей модели Title."""

    genre = rest_framework.CharFilter(field_name='genre__slug')
    category = rest_framework.CharFilter(field_name='category__slug')

    class Meta:
        model = Recipe
        fields = ('category', 'genre', 'name', 'year')