from django.urls import include, path

from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet

v1_router = DefaultRouter()
v1_router.register('users', CustomUserViewSet, basename='users')



urlpatterns = [
    path('', include(v1_router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]