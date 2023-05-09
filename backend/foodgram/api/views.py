from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework import viewsets, filters, permissions

from .serializers import TagSerializer, IngredientSerializer, RecipeSerializer
from recipes.models import Tag, Ingredient, Recipe


User = get_user_model()


class CustomUserViewSet(UserViewSet):

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if self.action == 'list' and not user.is_staff:
            queryset = queryset.exclude(is_staff=True)
        return queryset


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)
