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
    """Модель для ингридиентов"""
    name = models.CharField('Название', max_length=100)
    measurement_unit = models.CharField('Единица изменения', max_length=30)

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name


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
    # https://stackoverflow.com/questions/39576174/save-base64-image-in-django-file-field
    image = models.ImageField('Изображение', upload_to='photo/%Y/%m/%d/')
    tags = models.ManyToManyField(
        Tag, related_name='recipes', verbose_name='Тэги'
    )
    ingredients = models.ManyToManyField(
        Ingredient, related_name='recipes', verbose_name='Ингридиенты'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('name',)

    def __str__(self):
        return self.name

