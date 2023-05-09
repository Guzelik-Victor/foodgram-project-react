from django.urls import include, path

from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet, TagViewSet, IngredientViewSet, RecipeViewSet

v1_router = DefaultRouter()
v1_router.register('users', CustomUserViewSet, basename='users')
v1_router.register('tags', TagViewSet, basename='tags')
v1_router.register('ingredients', IngredientViewSet, basename='ingredients')
v1_router.register('recipes', RecipeViewSet, basename='recipes')
# v1_router.register(
#     r'recipes/(?P<recipe_id>\d+)/favorite',
#     FavoriteViewSet,
#     basename='favorites'
# )


urlpatterns = [
    path('', include(v1_router.urls)),
    # path('recipes/<int:recipe_id>/favorite/', FavoriteViewSet.as_view()),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
