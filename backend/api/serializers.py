import base64

from django.core.files.base import ContentFile
from django.db.models import Count
from djoser.serializers import UserSerializer
from rest_framework import serializers
from django.shortcuts import get_object_or_404

from app.models import Ingredient, Recipe, Tag
from users.models import User, Follow


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientsSerializerShort(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('name',)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class TagSerializerShort(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('name',)


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов"""
    author = UserSerializer(read_only=True,
                            default=serializers.CurrentUserDefault())
    image = Base64ImageField(required=False, allow_null=False)
    ingredients = IngredientsSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'name', 'text',
                  'cooking_time', 'image', 'tags', 'ingredients')
        read_only_fields = ('author',)


class RecipeSerializerShort(serializers.ModelSerializer):
    """Сериализатор для рецептов"""
    image = Base64ImageField(required=False, allow_null=False)
    tags = TagSerializerShort(many=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'tags')


class CustomUserSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name')


class FollowSerializer(serializers.ModelSerializer):
    follower = serializers.SlugRelatedField(
        slug_field='username',
        default=serializers.CurrentUserDefault(),
        read_only=True
    )
    following = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )

    def validate_following(self, following):
        if following.pk == self.context.get('request').user.pk:
            raise serializers.ValidationError(
                'Вы не можете подписаться сам на себя'
            )
        return following

    def to_representation(self, instance):
        user = instance.following
        user_recipes = user.recipes.all()
        recipes_count = user_recipes.count()

        user_serializer = CustomUserSerializer(user)
        recipes_serializer = RecipeSerializerShort(user_recipes, many=True)

        response = {}
        response.update(user_serializer.data)
        response['is_subscribed']: True
        response['recipes'] = recipes_serializer.data
        response['recipes_count'] = recipes_count
        return response

    class Meta:
        fields = ('follower', 'following')
        model = Follow
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=['follower', 'following'],
                message='Вы уже подписаны на этого автора.'
            )
        ]


class FollowUserSerializer(serializers.Serializer):
    following = serializers.SlugRelatedField(
        queryset=Follow.objects.all(), slug_field='username'
    )
    recipes = serializers.SerializerMethodField()

    def get_recipes(self, obj):
        recipes_filter = Recipe.objects.filter(author__follower=obj)
        return RecipeSerializerShort(recipes_filter, many=True).data
