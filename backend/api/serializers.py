import base64

from app.models import (
    FavoriteRecipe,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from django.core.files.base import ContentFile
from django.db import transaction
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from users.models import Follow, User


class Base64ImageField(serializers.ImageField):
    """Декодирование картинки"""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class CustomUserSerializer(UserSerializer):
    """Сериализатор для пользователей Djoiser"""
    is_subscribed = serializers.SerializerMethodField(default=True)

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False

        return user.follower.filter(following=obj.id).exists()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed')


class CustomUserRegisterSerializer(UserCreateSerializer):
    """Сериализатор для регистрации пользователей Djoiser"""
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'password', 'first_name',
                  'last_name')


class CustomUserProfileSerializer(UserSerializer):
    """Сериализатор для просмотра профиля пользователей Djoiser"""
    is_subscribed = serializers.SerializerMethodField(default=True)

    def get_is_subscribed(self, obj):
        author = get_object_or_404(User, username=obj.username)
        request = self.context.get('request')
        user = request.user
        # * Аноним может просматривать чужие профили
        if user.is_anonymous or author.pk == user.pk:
            return False

        return Follow.objects.filter(follower=user, following=author).exists()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed')


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор для ингридиентов"""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов"""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeIngredientGETSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source='ingredient.pk'
    )
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeGETSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов"""
    author = CustomUserSerializer(
        read_only=True, default=serializers.CurrentUserDefault()
    )
    tags = TagSerializer(many=True)
    image = Base64ImageField(required=False, allow_null=False)
    ingredients = RecipeIngredientGETSerializer(
        many=True, read_only=True, source='recipe_ingredient'
    )
    is_favorited = serializers.BooleanField(default=False)
    is_in_shopping_cart = serializers.BooleanField(default=False)

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'name', 'text',
                  'cooking_time', 'image', 'tags', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart')
        read_only_fields = ('author',)


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов (POST/DELETE/PATCH)"""
    author = serializers.SlugRelatedField(
        slug_field='username', default=serializers.CurrentUserDefault(),
        write_only=True, queryset=User.objects.all()
    )
    image = Base64ImageField(required=False, allow_null=False)
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())
    ingredients = RecipeIngredientSerializer(
        many=True, source='recipe_ingredient'
    )

    @transaction.atomic()
    def update(self, instance, validated_data):
        instance.ingredients.clear()
        instance.tags.clear()

        ingredients_data = validated_data.pop('recipe_ingredient')
        instance.tags.set(validated_data.get('tags', instance.tags))

        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=instance,
                ingredient_id=ingredient.get('id').pk,
                amount=ingredient.get('amount')
            ) for ingredient in ingredients_data
        ])

        return super().update(instance, validated_data)

    @transaction.atomic()
    def create(self, validated_data):
        ingredients_data = validated_data.pop('recipe_ingredient')
        tags_data = validated_data.pop('tags')

        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)

        for ingredient in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient.get('id'),
                amount=ingredient.get('amount')
            )

        return recipe

    def to_representation(self, instance):
        return RecipeGETSerializer(
            instance, context={'request': self.context.get('request')}
        ).data

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'ingredients', 'name', 'image', 'tags',
                  'text', 'cooking_time')
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Recipe.objects.all(),
                fields=['author', 'name'],
                message='У вас уже создан такой рецепт.'
            )
        ]


class RecipeSerializerShort(serializers.ModelSerializer):
    """Сериализатор для рецептов (укороченный)"""
    image = Base64ImageField(required=False, allow_null=False)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок"""
    id = serializers.ReadOnlyField(source='following.id')
    email = serializers.ReadOnlyField(source='following.email')
    username = serializers.ReadOnlyField(source='following.username')
    first_name = serializers.ReadOnlyField(source='following.first_name')
    last_name = serializers.ReadOnlyField(source='following.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = obj.following.recipes.all()
        if limit:
            queryset = queryset[:int(limit)]
        return RecipeSerializerShort(
            queryset, many=True, context={'request': request}
        ).data

    def get_recipes_count(self, obj):
        return obj.following.recipes.all().count()

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.follower.filter(following=obj.id).exists()

    class Meta:
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')
        model = Follow


class FollowCheckSubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор для проверки подписки"""
    class Meta:
        model = Follow
        fields = ('follower', 'following')

    def validate(self, obj):
        user = obj['follower']
        author = obj['following']
        is_subscribed = user.follower.filter(following=author).exists()

        if self.context.get('request').method == 'POST':
            if user == author:
                raise serializers.ValidationError(
                    {'errors': 'Подписка на самого себя не разрешена'}
                )
            if is_subscribed:
                raise serializers.ValidationError(
                    {'errors': 'Вы уже подписаны на этого автора'}
                )

        if self.context.get('request').method == 'DELETE':
            if user == author:
                raise serializers.ValidationError(
                    {'errors': 'Отписка от самого себя не разрешена'}
                )
            if not is_subscribed:
                raise serializers.ValidationError(
                    {'errors': 'Ошибка, вы уже отписались'}
                )

        return obj


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username', default=serializers.CurrentUserDefault(),
        read_only=True
    )
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all()
    )

    def validate(self, obj):
        user = self.context.get('request').user
        recipe = obj['recipe']
        favorite = user.favorites.filter(recipe=recipe).exists()

        if self.context.get('request').method == 'POST' and favorite:
            raise serializers.ValidationError(
                'Этот рецепт уже есть в избранном'
            )
        if self.context.get('request').method == 'DELETE' and not favorite:
            raise serializers.ValidationError(
                'Этого рецепта нет в избранном'
            )

        return obj

    class Meta:
        model = FavoriteRecipe
        fields = ('user', 'recipe',)


class ShoppingCartSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all()
    )

    def validate(self, obj):
        user = self.context['request'].user
        recipe = obj['recipe']
        cart = user.cart.filter(recipe=recipe).exists()

        if self.context.get('request').method == 'POST' and cart:
            raise serializers.ValidationError(
                'Этот рецепт уже добавлен в корзину'
            )
        if self.context.get('request').method == 'DELETE' and not cart:
            raise serializers.ValidationError(
                'Этот рецепт отсутствует в корзине'
            )
        return obj

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=['user', 'recipe'],
                message='Вы уже добавили рецепт в корзину.'
            )
        ]
