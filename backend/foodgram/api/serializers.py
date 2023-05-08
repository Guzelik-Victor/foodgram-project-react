from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework import serializers


from recipes.models import Tag, Ingredient, Recipe, IngredientRecipe, TagRecipe
from .serializers_fields import Hex2NameColor, Base64ImageField

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


class TagSerializer(serializers.ModelSerializer):
    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        extra_kwargs = {
            'name': {'read_only': True},
            'color': {'read_only': True},
            'slug': {'read_only': True},
        }


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
    tags = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = ('name', 'image', 'text', 'cooking_time', 'ingredients', 'tags')

    def to_representation(self, obj):
        self.fields['ingredients'] = IngredientSerializer(many=True)
        self.fields['tags'] = TagSerializer(many=True)
        self.fields['author'] = CustomUserSerializer()
        return super().to_representation(obj)

    def create(self, validated_data):
        request = self.context.get('request')
        user = USER.objects.get(id=request.user.id)
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=user, **validated_data)
        obj_tag_recipe = []
        obj_ingredient_recipe = []

        for ingredient in ingredients:
            obj_ingredient_recipe.append(
                IngredientRecipe(recipe=recipe, **ingredient)
            )
        IngredientRecipe.objects.bulk_create(obj_ingredient_recipe)

        for tag in tags:
            obj_tag_recipe.append(
                TagRecipe(recipe=recipe, *tag)
            )
        TagRecipe.objects.bulk_create(obj_tag_recipe)

        return recipe


    def update(self, instance, validated_data):
        ...