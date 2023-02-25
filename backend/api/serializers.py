from rest_framework import serializers
from app import models
from users.serializers import UserSerializer


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов"""
    author = UserSerializer()
    tags = TagSerializer(many=True)
    ingredients = IngredientsSerializer(many=True)
    # TODO: Добавить поля (is_favorited, is_in_shopping_cart)

    class Meta:
        model = models.Recipe
        fields = ('id', 'author', 'name', 'text',
                  'cooking_time', 'image', 'tags', 'ingredients')