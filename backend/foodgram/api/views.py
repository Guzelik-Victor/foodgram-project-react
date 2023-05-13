from django.contrib.auth import get_user_model
from django.http import HttpResponse
from djoser.views import UserViewSet
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .serializers import TagSerializer, IngredientSerializer, RecipeSerializer, FavoriteSerializer, SubscribeSerializer, ShoppingCartSerializer
from recipes.models import Tag, Ingredient, Recipe, Favorite, ShoppingCart
from users.models import Follow

from .filters import RecipeFilters, RecipeAnonymousFilters
from .permissions import AdminOrReadOnly, OwnerOrReadOnly
from .common import add_del_obj_action


User = get_user_model()


class CustomUserViewSet(UserViewSet):

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if self.action == 'list' and not user.is_staff:
            queryset = queryset.exclude(is_staff=True)
        return queryset

    @action(methods=['get'], detail=False, permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        followers = request.user.followers.all()
        serializer = SubscribeSerializer(followers, many=True)
        return Response(serializer.data)

    @action(methods=['post', 'delete'], detail=True, permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id):
        data = {
            'user': request.user.id,
            'author': id,
        }
        return add_del_obj_action(request, Follow, SubscribeSerializer, data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = (AdminOrReadOnly,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    permission_classes = (AdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    permission_classes = (OwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilters

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_anonymous:
            self.filterset_class = RecipeAnonymousFilters
        return qs

    @action(methods=['post', 'delete'], detail=True, permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk):
        data = {
            'user': request.user.id,
            'recipe': pk,
        }
        return add_del_obj_action(request, Favorite, FavoriteSerializer, data)

    @action(methods=['get'], detail=False, permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        user = request.user
        response = HttpResponse(
            content_type='text.txt; charset=utf-8',
            headers={'Content-Disposition': f'attachment; filename=f"{user.username}_shopping_cart.txt"'},

        )
        result_shopping_cart = dict()
        shopping_cart = user.shoppings.all()
        for recipe in shopping_cart:
            ingredients = recipe.recipe.ingredientrecipe_set.all()
            for item in ingredients:
                result_shopping_cart[item.ingredient.name] = (
                        result_shopping_cart.get(
                            item.ingredient.name,
                            {'measurement_unit': item.ingredient.measurement_unit}
                        )
                )
                result_shopping_cart[item.ingredient.name]['amount'] = (
                    result_shopping_cart[item.ingredient.name].get('amount', item.amount) + item.amount
                )

        for key, value in sorted(result_shopping_cart.items(), key=lambda x: x[0]):
            response.writelines(f'{key.capitalize()} ({value["measurement_unit"]}) - {value["amount"]};\n')

        return response

    @action(methods=['post', 'delete'], detail=True, permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk):
        data = {
            'user': request.user.id,
            'recipe': pk
        }
        return add_del_obj_action(request, ShoppingCart, ShoppingCartSerializer, data)


