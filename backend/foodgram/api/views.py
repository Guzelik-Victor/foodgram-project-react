

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from djoser.views import UserViewSet
from rest_framework import viewsets, filters, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import TagSerializer, IngredientSerializer, RecipeSerializer, FavoriteSerializer, SubscribeSerializer, ShoppingCartSerializer
from recipes.models import Tag, Ingredient, Recipe, Favorite, ShoppingCart
from users.models import Follow


User = get_user_model()


class CustomUserViewSet(UserViewSet):

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if self.action == 'list' and not user.is_staff:
            queryset = queryset.exclude(is_staff=True)
        return queryset

    @action(methods=['get'], detail=False)
    def subscriptions(self, request):
        followers = request.user.followers.all()
        serializer = SubscribeSerializer(followers, many=True)
        return Response(serializer.data)

    @action(methods=['post', 'delete'], detail=True)
    def subscribe(self, request, id):
        if request.method == 'POST':
            serializer = SubscribeSerializer(
                data={
                    'user': request.user.id,
                    'author': id,
                },
                context={'request': request},
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            following = Follow.objects.filter(
                user=request.user.id,
                author=id,
            )
            if following:
                following.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)


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

    @action(methods=['get'], detail=False)
    def favorites(self, request):
        favorites = request.user.favorites.all()
        serializer = FavoriteSerializer(favorites, many=True)
        return Response(serializer.data)

    @action(methods=['post', 'delete'], detail=True)
    def favorite(self, request, pk):
        if request.method == 'POST':
            serializer = FavoriteSerializer(
                data={
                    'user': request.user.id,
                    'recipe': pk,
                },
                context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            favorite = Favorite.objects.filter(
                user=request.user.id,
                recipe=pk,
            )
            if favorite:
                favorite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=False)
    def download_shopping_cart(self, request):
        user = request.user
        response = HttpResponse(
            content_type='text/csv',
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

    @action(methods=['post', 'delete'], detail=True)
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            serializer = ShoppingCartSerializer(
                data={
                    'user': request.user.id,
                    'recipe': pk,
                },
                context={'request': request},
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            shopping_obj = ShoppingCart.objects.filter(
                user=request.user.id,
                recipe=pk,
            )
            if shopping_obj:
                shopping_obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)


