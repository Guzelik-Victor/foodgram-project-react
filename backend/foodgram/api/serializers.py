from django.conf import settings
from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer, UserCreateSerializer, TokenCreateSerializer

user = get_user_model()


class CustomUserSerializer(UserSerializer):

    class Meta:
        model = user
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'password')
        extra_kwargs = {
            'password': {'write_only': True},
        }


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = user
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'password')