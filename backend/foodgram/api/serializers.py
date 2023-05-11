from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import Tag, Ingredient, Recipe, IngredientRecipe, TagRecipe, Favorite
from users.models import Follow
from .serializers_fields import Hex2NameColor, Base64ImageField, TagListField

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
        follower = user.followers.filter(author=obj.id).exists()
        return follower


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = USER
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'password')


class TagSerializer(serializers.ModelSerializer):
    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class AddIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = AddIngredientSerializer(many=True)
    tags = TagListField()
    image = Base64ImageField(required=False, allow_null=True)
    author = serializers.PrimaryKeyRelatedField(
        read_only=True, default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name', 'image', 'text', 'cooking_time')

    def to_representation(self, obj):
        self.fields['ingredients'] = IngredientSerializer(many=True, source='ingredient')
        self.fields['tags'] = TagSerializer(many=True, source='tag')
        self.fields['author'] = CustomUserSerializer()
        return super().to_representation(obj)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        obj_tag_recipe = []
        obj_ingredient_recipe = []

        for ingredient in ingredients:
            obj_ingredient_recipe.append(
                IngredientRecipe(recipe=recipe, **ingredient)
            )
        IngredientRecipe.objects.bulk_create(obj_ingredient_recipe)

        for tag in tags.values():
            obj_tag_recipe.append(
                TagRecipe(recipe=recipe, tag=tag)
            )
        TagRecipe.objects.bulk_create(obj_tag_recipe)

        return recipe

    def update(self, instance, validated_data):

        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
            )

        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        IngredientRecipe.objects.filter(recipe=instance).delete()
        TagRecipe.objects.filter(recipe=instance).delete()

        obj_tag_recipe = []
        obj_ingredient_recipe = []

        for ingredient in ingredients:
            obj_ingredient_recipe.append(
                IngredientRecipe(recipe=instance, **ingredient)
            )
        IngredientRecipe.objects.bulk_create(obj_ingredient_recipe)

        for tag in tags.values():
            obj_tag_recipe.append(
                TagRecipe(recipe=instance, tag=tag)
            )
        TagRecipe.objects.bulk_create(obj_tag_recipe)

        instance.save()
        return instance


class RecipeNestedSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = serializers.ReadOnlyField(source='recipe.image.url')
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = Favorite
        fields = ('user', 'recipe', 'id', 'name', 'image', 'cooking_time')
        extra_kwargs = {
            'user': {'write_only': True},
            'recipe': {'write_only': True},
        }
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe')
            )
        ]


class SubscribeSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

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
        serializer = RecipeNestedSerializer(queryset, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()

    def get_is_subscribed(self, obj):
        return True

    def validate(self, data):
        if data['user'] == data['author']:
            raise serializers.ValidationError('Нельзя подписаться на себя!')
        return data





