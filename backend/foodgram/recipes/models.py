from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.db.models import UniqueConstraint

user = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(max_length=254, db_index=True)
    measurement_unit = models.CharField(max_length=128)


class Tag(models.Model):
    name = models.CharField(max_length=200, unique=True, db_index=True)
    color = models.CharField(
        max_length=7,
        unique=True,
    )
    slug = models.SlugField(max_length=200, unique=True)


class Recipe(models.Model):
    author = models.ForeignKey(
        user,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    name = models.CharField('name', max_length=200)
    image = models.ImageField('image', upload_to='recipes/images/', null=True, default=None)
    text = models.TextField(max_length=512)
    cooking_time = models.IntegerField(validators=[MinValueValidator(1)])
    ingredient = models.ManyToManyField(Ingredient, through='IngredientRecipe')
    tag = models.ManyToManyField(Tag, through='TagRecipe')


class TagRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)


class IngredientRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField()


class Favorite(models.Model):
    user = models.ForeignKey(
        user,
        related_name='favorites',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='favorites',
        on_delete=models.CASCADE,
    )

    class Meta:
        UniqueConstraint(fields=['user', 'recipe'], name='unique_recipe')


class ShoppingList(models.Model):
    user = models.ForeignKey(
        user,
        related_name='shopping',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='shopping',
        on_delete=models.CASCADE,
    )
