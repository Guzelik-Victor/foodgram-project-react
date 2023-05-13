from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.db.models import UniqueConstraint

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(max_length=254, db_index=True)
    measurement_unit = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=200, unique=True, db_index=True)
    color = models.CharField(
        max_length=7,
        unique=True,
        null=True,
        validators=[RegexValidator(r'^#[A-Fa-f0-9]{6}$')],
    )
    slug = models.SlugField(max_length=200, unique=True, null=True)

    def __str__(self):
        return self.slug


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    name = models.CharField('name', max_length=200)
    image = models.ImageField('image', upload_to='recipes/images/', null=True, default=None)
    text = models.TextField(max_length=512)
    cooking_time = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    pub_date = models.DateTimeField(auto_now_add=True)
    ingredient = models.ManyToManyField(Ingredient, through='IngredientRecipe')
    tag = models.ManyToManyField(Tag, through='TagRecipe')

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class TagRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)


class IngredientRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField()


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        related_name='favorites',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='favorites',
        on_delete=models.CASCADE,
    )

    class Meta:
        UniqueConstraint(fields=['user', 'recipe'], name='unique_favorite_recipe')

    def __str__(self):
        return f'{self.user} - {self.recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        related_name='shoppings',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='shoppings',
        on_delete=models.CASCADE,
    )

    class Meta:
        UniqueConstraint(fields=['user', 'recipe'], name='unique_shopping_cart')

    def __str__(self):
        return f'{self.user} - {self.recipe}'
