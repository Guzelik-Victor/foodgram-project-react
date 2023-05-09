from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework import viewsets, filters, permissions, mixins, status
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import TagSerializer, IngredientSerializer, RecipeSerializer, FavoriteSerializer, RecipeNestedSerializer
from recipes.models import Tag, Ingredient, Recipe, Favorite


User = get_user_model()


class CustomUserViewSet(UserViewSet):

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if self.action == 'list' and not user.is_staff:
            queryset = queryset.exclude(is_staff=True)
        return queryset

    # @action(methods=['list'])
    # def subscriptions(self, request):
    #     self.queryset = self.queryset.


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

    @action(methods=['post', 'delete'], detail=True)
    def favorite(self, request, pk):
        recipe = Recipe.objects.get(id=pk)
        user_id = request.user.id
        if request.method == 'POST':
            serializer = FavoriteSerializer(
                data={
                    'user': user_id,
                    'recipe': recipe.id,
                })
            if serializer.is_valid():
                serializer.save()
                data = {
                    'id': recipe.id,
                    'name': recipe.text,
                    'image': recipe.image,
                    'cooking_time': recipe.cooking_time,
                }
                serializer = RecipeNestedSerializer(data=data)
                if serializer.is_valid():
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            favorite = Favorite.objects.filter(
                user=user_id,
                recipe=pk,
            )
            if favorite:
                favorite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)





