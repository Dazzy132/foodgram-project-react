from colorfield.fields import ColorField
from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Tag(models.Model):
    """Модель для тегов"""
    name = models.CharField('Название', max_length=100, unique=True)
    color = ColorField(
        verbose_name='Цвет тега', default='#FF0000', format='hex', unique=True
    )
    slug = models.SlugField('slug', max_length=100, unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель для ингредиентов"""
    name = models.CharField('Название', max_length=100)
    measurement_unit = models.CharField('Единица изменения', max_length=30)

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ('pk',)

    def __str__(self):
        return f'{self.name} | {self.measurement_unit}'


class Recipe(models.Model):
    """Модель для рецептов"""
    author = models.ForeignKey(
        User, on_delete=models.PROTECT,
        verbose_name='Автор', related_name='recipes',
    )
    name = models.CharField('Название', max_length=200)
    text = models.TextField('Описание')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления', help_text='В минутах',
        validators=[MinValueValidator(
            1, 'Время приготовления не может быть меньше 1 минуты')
        ]
    )
    image = models.ImageField('Изображение', upload_to='recipes/')
    tags = models.ManyToManyField(
        Tag, related_name='recipes', verbose_name='Теги'
    )
    ingredients = models.ManyToManyField(
        Ingredient, related_name='recipes', verbose_name='Ингридиенты',
        through='RecipeIngredient'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('id',)

    def __str__(self):
        return f'Рецепт - {self.name} | Автор рецепта - {self.author.username}'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='recipe_ingredient',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name='recipe_ingredient',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество', default=1,
        validators=[MinValueValidator(1, 'Минимальное количество - 1')]
    )

    class Meta:
        verbose_name = 'Кол-во ингридиентов в рецепте'
        verbose_name_plural = 'Кол-во ингридиентов в рецепте'

    def __str__(self):
        return (f'Рецепт {self.recipe.name} | {self.ingredient.name} -'
                f' {self.amount}')


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe, related_name='favorites', verbose_name='Любимый рецепт',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe'
            )
        ]

    def __str__(self):
        return (f'У {self.user} избранный рецепт - {self.recipe.name}'
                f' от {self.recipe.author.username}')


class ShoppingCart(models.Model):
    """Модель список покупок"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Корзина продуктов'
        verbose_name_plural = 'Корзины продуктов'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_cart_user'
            )
        ]

    def __str__(self):
        return (
            f'Пользователь {self.user} | Рецепт {self.recipe}'
            f' от {self.recipe.name}'
        )

