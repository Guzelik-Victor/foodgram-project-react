from django_filters import rest_framework
from recipes.models import Ingredient, Recipe, Tag


class RecipeAnonymousFilters(rest_framework.FilterSet):
    """Воможность фильтровать рецепты только по тэгу
    для анонимных пользователей."""

    tags = rest_framework.ModelMultipleChoiceFilter(
        field_name='tag__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug',
    )

    class Meta:
        model = Recipe
        fields = ('tags',)


class RecipeFilters(RecipeAnonymousFilters):
    """Фильтрация рецептов для авторизованных пользователей."""

    is_favorited = rest_framework.BooleanFilter(
        field_name='favorites',
        method='get_filter_queryset',
        label='favorites',
    )
    is_in_shopping_cart = rest_framework.BooleanFilter(
        field_name='shoppings',
        method='get_filter_queryset',
        label='shopping cart',
    )
    author = rest_framework.NumberFilter(field_name='author__id')

    class Meta:
        model = RecipeAnonymousFilters.Meta.model
        fields = RecipeAnonymousFilters.Meta.fields + ('author',)

    def get_filter_queryset(self, queryset, field_name, value):
        user = self.request.user
        if not value:
            return queryset
        return queryset.filter(
            id__in=user.favorites.values_list('recipe')
            if field_name == 'favorites'
            else user.shoppings.values_list('recipe')
        )


class IngredientFilter(rest_framework.FilterSet):
    name = rest_framework.CharFilter(
        field_name='name',
        lookup_expr='istartswith'
    )

    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit')
