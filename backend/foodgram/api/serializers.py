from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag, TagRecipe)
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from users.models import Follow
from .common import create_update_instance_recipe, get_is_field_action
from .serializers_fields import Base64ImageField, TagListField

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subscribed',
        )
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        data = {
            'author': obj.id
        }
        return get_is_field_action(request, Follow, data)


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient.id'
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def validate_amount(self, value):
        if int(value) < 1:
            raise serializers.ValidationError(
                'Количество ингредиента должно быть больше нуля!'
            )
        return value


class RecipeViewSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True, source='tag')
    ingredients = serializers.SerializerMethodField(
        read_only=True,
        source='get_ingredients'
    )
    is_favorited = serializers.SerializerMethodField(
        read_only=True,
        source='get_is_favorited'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        read_only=True,
        source='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_ingredients(self, obj):
        ingredients = IngredientRecipe.objects.filter(recipe=obj)
        return IngredientInRecipeSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        data = {
            'recipe': obj.id
        }
        return get_is_field_action(request, Favorite, data)

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        data = {
            'recipe': obj.id
        }
        return get_is_field_action(request, ShoppingCart, data)


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientInRecipeSerializer(many=True)
    tags = TagListField()
    image = Base64ImageField(required=False, allow_null=True)
    author = serializers.PrimaryKeyRelatedField(
        read_only=True, default=serializers.CurrentUserDefault()
    )
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)

        create_update_instance_recipe(recipe, ingredients, tags)

        return recipe

    def update(self, instance, validated_data):

        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        TagRecipe.objects.filter(recipe=instance).delete()
        IngredientRecipe.objects.filter(recipe=instance).delete()

        create_update_instance_recipe(instance, ingredients, tags)

        return super().update(instance, validated_data)

    def validate_ingredients(self, value):

        if not value:
            raise serializers.ValidationError('Укажите ингредиенты')
        unique_id = [v['ingredient'].get('id') for v in value]
        if len(value) > len(set(unique_id)):
            raise serializers.ValidationError(
                'Для одного блюда указывать более одного'
                'раза один и тот же ингредиент - недопустимо'
            )

        return value

    def to_representation(self, instance):
        return RecipeViewSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data


class RecipeNestedSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(
        use_url=True,
        allow_null=True,
        required=False,
    )

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')

    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Follow
        fields = (
            'user',
            'author',
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        extra_kwargs = {
            'user': {'write_only': True},
            'author': {'write_only': True},
        }
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'author'),
            )
        ]

    def get_recipes(self, obj):
        queryset = Recipe.objects.filter(author=obj.author)
        serializer = RecipeNestedSerializer(
            queryset,
            many=True,
            context={'request': self.context.get('request')},
        )
        return serializer.data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()

    def get_is_subscribed(self, obj):
        return True

    def validate(self, data):
        if data['user'] == data['author']:
            raise serializers.ValidationError(
                'Нельзя подписаться на себя!'
            )
        return data


class FavoriteShoppingCartSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = serializers.ImageField(
        use_url=True,
        allow_null=True,
        required=False,
        source='recipe.image',
    )
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = Favorite
        fields = ('user', 'recipe', 'id', 'name', 'image', 'cooking_time')
        extra_kwargs = {
            'user': {'write_only': True},
            'recipe': {'write_only': True},
            'image': {'read_only': True},
        }

    def validate(self, data):
        obj_exists = self.Meta.model.objects.filter(
            user=data['user'],
            recipe=data['recipe']
        ).exists()
        if not obj_exists:
            return data
        model_name = (
            'избранное' if self.Meta.model == Favorite
            else 'список покупок'
        )
        raise serializers.ValidationError(
            f'Рецепт уже добавлен в {model_name}'
        )


class FavoriteSerializer(FavoriteShoppingCartSerializer):
    pass


class ShoppingCartSerializer(FavoriteShoppingCartSerializer):

    class Meta:
        model = ShoppingCart
        fields = FavoriteShoppingCartSerializer.Meta.fields
        extra_kwargs = FavoriteShoppingCartSerializer.Meta.extra_kwargs
