import base64

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from app.models import (FavoriteRecipe, Ingredient, Recipe, RecipeIngredient,
                        Tag, UserProductList)
from users.models import Follow, User


class Base64ImageField(serializers.ImageField):
    """Декодирование картинки"""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


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


class CustomUserSerializer(UserSerializer):
    """Сериализатор для пользователей Djoiser"""
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
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed')


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

    def get_is_favorited(self, obj):
        test = self.context.get('request').user
        if test.is_anonymous:
            return False

        return FavoriteRecipe.objects.filter(
            recipe=obj, user=self.context.get('request').user
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        test = self.context.get('request').user
        if test.is_anonymous:
            return False

        return UserProductList.objects.filter(
            recipe=obj, user=self.context.get('request').user
        ).exists()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'name', 'text',
                  'cooking_time', 'image', 'tags', 'ingredients',
                  )
        read_only_fields = ('author',)


class RecipePOSTSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов (укороченный)"""
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

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.tags.set(validated_data.get('tags', instance.tags))

        ingredients_data = validated_data.get(
            'recipe_ingredient', instance.ingredients
        )

        instance.ingredients.clear()

        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=instance,
                ingredient_id=ingredient.get('id').pk,
                amount=ingredient.get('amount')
            ) for ingredient in ingredients_data
        ])

        instance.save()
        return instance

    def create(self, validated_data):
        ingredients_data = validated_data.pop('recipe_ingredient')
        tags_data = validated_data.pop('tags')

        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)

        for ingredient in ingredients_data:
            ing = get_object_or_404(Ingredient, name=ingredient.get('id').name)
            amount = ingredient.get('amount')

            RecipeIngredient.objects.create(
                recipe=recipe, ingredient=ing, amount=amount
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

    def validate_following(self, following):
        """Проверка на то, чтобы пользователи не могли подписываться на себя"""
        if following.pk == self.context.get('request').user.pk:
            raise serializers.ValidationError(
                'Вы не можете подписаться сам на себя'
            )
        return following

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = obj.following.recipes.all()
        if limit:
            queryset = queryset[:int(limit)]
        return RecipeGETSerializer(
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


class FollowUserSerializer(serializers.Serializer):
    """Сериализатор для POST запроса, который выведет информацию об авторе и
    его рецептов"""
    following = serializers.SlugRelatedField(
        queryset=Follow.objects.all(), slug_field='username'
    )
    recipes = serializers.SerializerMethodField()

    def get_recipes(self, obj):
        recipes_filter = Recipe.objects.filter(author__follower=obj)
        return RecipeGETSerializer(recipes_filter, many=True).data


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username', default=serializers.CurrentUserDefault(),
        read_only=True
    )
    recipe = RecipeGETSerializer(read_only=True)

    class Meta:
        model = FavoriteRecipe
        fields = ('user', 'recipe',)
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=FavoriteRecipe.objects.all(),
                fields=['user', 'recipe'],
                message='Вы уже добавили рецепт в корзину.'
            )
        ]


class UserProductListSerializer(serializers.ModelSerializer):
    recipe = RecipeSerializerShort(read_only=True)

    class Meta:
        model = UserProductList
        fields = ('recipe',)
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=UserProductList.objects.all(),
                fields=['user', 'recipe'],
                message='Вы уже добавили рецепт в корзину.'
            )
        ]
