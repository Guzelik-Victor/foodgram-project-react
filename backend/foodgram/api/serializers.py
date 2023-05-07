from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework import serializers

from users.models import Follow

USER = get_user_model()


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = USER
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'password', 'is_subscribed')
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def get_is_subscribed(self, obj):
        user = None
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = USER.objects.get(id=request.user.id) if request.user.id else None
        if not user:
            return False
        following = user.follower.values_list('author_id', flat=True)
        return obj.id in following


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = USER
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'password')

