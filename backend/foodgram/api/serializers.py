from rest_framework import serializers
from app import models


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Tag
        fields = ('name', 'slug', 'color')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов"""
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    # tags = TagSerializer(many=True)

    class Meta:
        model = models.Recipe
        fields = ('id', 'author', 'name', 'text',
                  'cooking_time', 'image', 'tags', 'ingredients')