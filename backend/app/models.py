from colorfield.fields import ColorField
from django.db import models

from users.models import User


class Tag(models.Model):
    """Модель для тегов"""
    name = models.CharField('Название', max_length=100, unique=True)
    # https://qna.habr.com/q/591090
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
        'Время приготовления', help_text='В минутах'
    )
    image = models.ImageField('Изображение', upload_to='recipes/')
    tags = models.ManyToManyField(
        Tag, related_name='recipes', verbose_name='Тэги'
    )
    ingredients = models.ManyToManyField(
        Ingredient, related_name='recipes', verbose_name='Ингридиенты',
        through='RecipeIngredient'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} | Автор - {self.author.username}'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='recipe_ingredient'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name='recipe_ingredient'
    )
    amount = models.PositiveSmallIntegerField()

    class Meta:
        verbose_name = 'Кол-во ингридиентов в рецепте'
        verbose_name_plural = 'Кол-во ингридиентов в рецепте'

    def __str__(self):
        return f'{self.recipe.name} - {self.ingredient.name} - {self.amount}'


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe, related_name='favorites', verbose_name='Любимые рецепты',
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
        return f'{self.user} - {self.recipe.name}'


class UserProductList(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='products',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe, related_name='products', verbose_name='Рецепт',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Корзина продуктов'
        verbose_name_plural = 'Корзины продуктов'

    def __str__(self):
        return f'{self.user} - рецепт {self.recipe.name} - автора ' \
               f'{self.recipe.author.username}'

