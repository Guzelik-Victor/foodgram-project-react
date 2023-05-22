from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import Follow
from .common import add_del_obj_action
from .filters import IngredientFilter, RecipeAnonymousFilters, RecipeFilters
from .pagination import CustomPagination
from .permissions import AdminOrReadOnly, OwnerOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          ShoppingCartSerializer, SubscribeSerializer,
                          TagSerializer)

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'list' and not self.request.user.is_staff:
            return queryset.exclude(is_staff=True)
        return queryset

    @action(
        methods=('get',),
        url_path='me',
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def get_self_page(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        followers = self.paginate_queryset(request.user.followers.all())
        serializer = SubscribeSerializer(
            followers,
            many=True,
            context={'request': request},
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id):
        data = {
            'user': request.user.id,
            'author': id,
        }
        return add_del_obj_action(
            request,
            Follow,
            SubscribeSerializer,
            data,
        )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = (AdminOrReadOnly,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    permission_classes = (AdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (OwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilters
    pagination_class = CustomPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        if self.request.user.is_anonymous:
            self.filterset_class = RecipeAnonymousFilters
        return super().get_queryset()

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk):
        data = {
            'user': request.user.id,
            'recipe': pk,
        }
        return add_del_obj_action(
            request,
            Favorite,
            FavoriteSerializer,
            data,
        )

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticated,),

    )
    def download_shopping_cart(self, request):
        user = request.user
        text = 'Cписок покупок: \n'

        shopping_cart = IngredientRecipe.objects.filter(
            recipe_id__in=user.shoppings.values_list('recipe_id', flat=True)
        ).values_list(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(Sum('amount'))

        for index, ingredient in enumerate(sorted(shopping_cart), start=1):
            text += f'{index}. {ingredient[0].capitalize()} ' \
                    f'({ingredient[1]}) - {ingredient[2]};\n'

        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping-list.txt"'
        )

        return response

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk):
        data = {
            'user': request.user.id,
            'recipe': pk
        }
        return add_del_obj_action(
            request,
            ShoppingCart,
            ShoppingCartSerializer,
            data,
        )
