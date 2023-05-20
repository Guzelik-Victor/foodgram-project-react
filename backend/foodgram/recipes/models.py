from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField('Название', max_length=254, db_index=True)
    measurement_unit = models.CharField('Ед. измерения', max_length=128)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.id}, {self.name}'


class Tag(models.Model):
    name = models.CharField(
        'Название',
        max_length=200,
        unique=True,
        db_index=True,
    )
    color = models.CharField(
        'Цвет',
        max_length=7,
        unique=True,
        null=True,
        validators=[RegexValidator(r'^#[A-Fa-f0-9]{6}$')],
    )
    slug = models.SlugField(
        'Уникальное название',
        max_length=200,
        unique=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Tэг'
        verbose_name_plural = 'Tэги'

    def __str__(self):
        return self.slug


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    name = models.CharField('Название', max_length=200)
    image = models.ImageField(
        'Фото',
        upload_to='recipes/images/',
        null=True,
        default=None,
    )
    text = models.TextField('Описание', max_length=512)
    cooking_time = models.PositiveIntegerField(
        'Время приготавления',
        validators=[MinValueValidator(1)],
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    ingredient = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        verbose_name='Ингридиенты'
    )
    tag = models.ManyToManyField(
        Tag,
        through='TagRecipe',
        verbose_name='Тэги',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class TagRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'tag'], name='unique_tag_for_recipe'
            )
        ]


class IngredientRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='recipes',
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='ingredients',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField('Количество')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient_for_recipe',
            )
        ]

    def __str__(self):
        return (f'{self.recipe.name}: '
                f'{self.ingredient.name} - '
                f'{self.amount} '
                f'{self.ingredient.measurement_unit}')


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        related_name='favorites',
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='favorites',
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorite_recipe'
            )
        ]

    def __str__(self):
        return f'{self.user} - {self.recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        related_name='shoppings',
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='shoppings',
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_shopping_cart'
            )
        ]

    def __str__(self):
        return f'{self.user} - {self.recipe}'
